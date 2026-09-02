#!/usr/bin/env python3
"""
fix_receiver_exported.py

Corrige o crash:
  SecurityException: One of RECEIVER_EXPORTED or RECEIVER_NOT_EXPORTED
  should be specified when a receiver isn't being registered
  exclusively for system broadcasts

Causa: a partir do Android 13 (Tiramisu, API 33), TODO registerReceiver()
que roda em runtime (não é um <receiver> declarado no Manifest) precisa
declarar explicitamente se aceita broadcasts de fora do app
(RECEIVER_EXPORTED) ou só do próprio processo (RECEIVER_NOT_EXPORTED).

O código do app tinha 11 chamadas registerReceiver() feitas nos tempos
do Android 1.6 (Donut), quando essa exigência não existia. Só uma
(em MediaPlaybackService.java) já tinha sido corrigida manualmente.

Este script classifica e corrige as outras 10, em 8 arquivos,
usando o próprio IntentFilter de cada uma para decidir o flag certo:

  - Filtros com ações do SISTEMA Android
    (Intent.ACTION_MEDIA_SCANNER_STARTED/FINISHED, ACTION_MEDIA_UNMOUNTED,
    ACTION_MEDIA_EJECT, ACTION_MEDIA_MOUNTED)
    -> RECEIVER_EXPORTED (o broadcast vem de fora do processo do app,
       do próprio Android; sem isso o app pararia de recebê-los).

  - Filtros com ações INTERNAS do próprio MediaPlaybackService
    (META_CHANGED, QUEUE_CHANGED, PLAYSTATE_CHANGED, PLAYBACK_COMPLETE,
    ASYNC_OPEN_COMPLETE) -- confirmado que só existe um sendBroadcast()
    no projeto inteiro, dentro do próprio MediaPlaybackService
    -> RECEIVER_NOT_EXPORTED (broadcast nunca sai do processo do app).

O flag é adicionado condicionalmente para SDK_INT >= TIRAMISU, com
fallback para o registerReceiver(receiver, filter) antigo em versões
anteriores -- mesmo padrão que já existia em MediaPlaybackService.java.

Faz backup (.bak5) de cada arquivo antes de editar. Idempotente.

Uso (dentro do Termux, na pasta do projeto Music):
  python fix_receiver_exported.py
ou apontando o caminho do repo:
  python fix_receiver_exported.py /caminho/para/Music
"""

import sys
import os
import re
import shutil

PKG_REL = os.path.join("com", "android", "music")

SYSTEM_ACTIONS = (
    "Intent.ACTION_MEDIA_SCANNER_STARTED",
    "Intent.ACTION_MEDIA_SCANNER_FINISHED",
    "Intent.ACTION_MEDIA_UNMOUNTED",
    "Intent.ACTION_MEDIA_EJECT",
    "Intent.ACTION_MEDIA_MOUNTED",
)

# arquivo -> lista de (receiver_var, filter_expr_no_call) a corrigir
# filter_expr_no_call é exatamente o texto do 2º argumento passado hoje
# ao registerReceiver, usado para localizar a chamada com precisão.
TARGETS = {
    "AlbumBrowserActivity.java": [
        ("mScanListener", "f"),
        ("mTrackListListener", "f"),
    ],
    "ArtistAlbumBrowserActivity.java": [
        ("mScanListener", "f"),
        ("mTrackListListener", "f"),
    ],
    "MediaPlaybackActivity.java": [
        ("mStatusListener", "new IntentFilter(f)"),
    ],
    "MediaPlaybackService.java": [
        ("mUnmountReceiver", "iFilter"),
    ],
    "MusicBrowserActivity.java": [
        ("mStatusListener", "new IntentFilter(f)"),
    ],
    "PlaylistBrowserActivity.java": [
        ("mScanListener", "f"),
    ],
    "QueryBrowserActivity.java": [
        ("mScanListener", "f"),
    ],
    "StreamStarter.java": [
        ("mStatusListener", "new IntentFilter(f)"),
    ],
    "TrackBrowserActivity.java": [
        ("mScanListener", "f"),
        ("mNowPlayingListener", "new IntentFilter(f)"),
        ("mTrackListListener", "new IntentFilter(f)"),
    ],
}


def backup(path):
    bak = path + ".bak5"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print(f"[+] Backup criado: {bak}")


def classify(content, call_start_idx):
    """
    Olha para trás a partir do início da chamada registerReceiver
    e procura o addAction mais próximo para decidir se é filtro de
    sistema ou interno. Considera até 800 caracteres antes da chamada
    (cobre blocos de IntentFilter típicos deste projeto).
    """
    window = content[max(0, call_start_idx - 800):call_start_idx]
    for action in SYSTEM_ACTIONS:
        if action in window:
            return "EXPORTED"
    return "NOT_EXPORTED"


def fix_file(base_dir, filename, targets):
    path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, filename)
    if not os.path.isfile(path):
        print(f"[!] Não encontrei {path}. Pulando.")
        return False

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    changed = False
    for receiver_var, filter_expr in targets:
        already_fixed_re = re.compile(
            rf"if\s*\(Build\.VERSION\.SDK_INT >= Build\.VERSION_CODES\.TIRAMISU\)\s*\{{\s*"
            rf"registerReceiver\({re.escape(receiver_var)},\s*{re.escape(filter_expr)},\s*"
            rf"Context\.RECEIVER_(EXPORTED|NOT_EXPORTED)\);"
        )
        m_fixed = already_fixed_re.search(content)
        if m_fixed:
            print(f"[=] {filename}: {receiver_var} já está corrigido.")
            continue

        plain_call = f"registerReceiver({receiver_var}, {filter_expr});"
        idx = content.find(plain_call)

        if idx == -1:
            print(f"[!] Não encontrei '{plain_call}' em {filename} "
                  f"(nem uma versão já corrigida). Revise manualmente esse ponto.")
            continue

        flag = classify(content, idx)

        # descobre a indentação da linha original para manter o estilo
        line_start = content.rfind("\n", 0, idx) + 1
        indent = content[line_start:idx]
        indent = indent if indent.strip() == "" else "        "

        replacement = (
            f"if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {{\n"
            f"{indent}    registerReceiver({receiver_var}, {filter_expr}, Context.RECEIVER_{flag});\n"
            f"{indent}}} else {{\n"
            f"{indent}    registerReceiver({receiver_var}, {filter_expr});\n"
            f"{indent}}}"
        )

        content = content[:idx] + replacement + content[idx + len(plain_call):]
        print(f"[+] {filename}: {receiver_var} -> RECEIVER_{flag}")
        changed = True

    if not changed:
        return False

    # garante imports necessários
    needs_build_import = "import android.os.Build;" not in content
    needs_context_import = "import android.content.Context;" not in content

    if needs_build_import or needs_context_import:
        # insere após o último import existente
        import_lines = list(re.finditer(r"^import .+;$", content, re.MULTILINE))
        if import_lines:
            insert_at = import_lines[-1].end()
            to_add = ""
            if needs_context_import:
                to_add += "\nimport android.content.Context;"
            if needs_build_import:
                to_add += "\nimport android.os.Build;"
            content = content[:insert_at] + to_add + content[insert_at:]
            if needs_context_import:
                print(f"[+] {filename}: import android.content.Context; adicionado")
            if needs_build_import:
                print(f"[+] {filename}: import android.os.Build; adicionado")

    backup(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def main():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    base_dir = os.path.abspath(base_dir)
    print(f"[i] Repositório alvo: {base_dir}\n")

    any_change = False
    for filename, targets in TARGETS.items():
        any_change |= fix_file(base_dir, filename, targets)

    print()
    print("=" * 60)
    if any_change:
        print("Correções aplicadas. Agora rode:")
        print()
        print("  ./gradlew clean assembleDebug")
        print()
        print("Depois reinstale e teste o app -- os dois crashes reportados")
        print("(MusicBrowserActivity.onResume e MediaPlaybackService.onCreate)")
        print("devem estar resolvidos.")
    else:
        print("Nada para corrigir (já estava tudo aplicado).")
    print("=" * 60)


if __name__ == "__main__":
    main()
