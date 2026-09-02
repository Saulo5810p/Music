#!/usr/bin/env python3
"""
fix_kotlin_duplicate.py

Corrige o erro de build:
  Duplicate class kotlin.collections.jdk8.CollectionsJDK8Kt found in modules
  kotlin-stdlib-1.8.22.jar ... e kotlin-stdlib-jdk8-1.6.21.jar ...

Causa: uma dependência transitiva (geralmente androidx.media) ainda arrasta
kotlin-stdlib-jdk7 / kotlin-stdlib-jdk8 (1.6.21), que hoje já vêm embutidas
no kotlin-stdlib principal (1.8.22+), gerando classes duplicadas.

O que o script faz:
  1. Localiza app/build.gradle (relativo ao diretório onde é executado,
     ou você pode passar o caminho do repo como argumento).
  2. Insere um bloco `configurations.all { exclude ... }` para excluir
     kotlin-stdlib-jdk7 e kotlin-stdlib-jdk8 de todo o classpath.
  3. Faz backup do arquivo original (.bak) antes de editar.
  4. É idempotente: rodar de novo não duplica o bloco.

Uso (dentro do Termux, na pasta do projeto Music):
  python fix_kotlin_duplicate.py
ou apontando o caminho do repo:
  python fix_kotlin_duplicate.py /caminho/para/Music
"""

import sys
import os
import re
import shutil

MARKER = "// >>> fix_kotlin_duplicate.py: exclude old kotlin-stdlib-jdk7/jdk8"
MARKER_END = "// <<< fix_kotlin_duplicate.py"

EXCLUDE_BLOCK = f"""
{MARKER}
configurations.all {{
    exclude group: 'org.jetbrains.kotlin', module: 'kotlin-stdlib-jdk7'
    exclude group: 'org.jetbrains.kotlin', module: 'kotlin-stdlib-jdk8'
}}
{MARKER_END}
"""


def find_app_build_gradle(base_dir: str) -> str:
    candidates = [
        os.path.join(base_dir, "app", "build.gradle"),
        os.path.join(base_dir, "app", "build.gradle.kts"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    raise FileNotFoundError(
        f"Não encontrei app/build.gradle (ou .kts) dentro de {base_dir}. "
        "Rode o script na raiz do repo clonado (pasta 'Music') ou passe o caminho como argumento."
    )


def already_patched(content: str) -> bool:
    return MARKER in content


def patch(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if already_patched(content):
        print(f"[=] {path} já está corrigido, nada a fazer.")
        return False

    backup_path = path + ".bak"
    if not os.path.exists(backup_path):
        shutil.copy2(path, backup_path)
        print(f"[+] Backup criado: {backup_path}")

    # Insere o bloco logo após a abertura do bloco `android { ... }`
    # se existir, senão anexa no fim do arquivo (funciona nos dois casos
    # pois configurations.all é top-level do módulo).
    new_content = content.rstrip() + "\n" + EXCLUDE_BLOCK

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[+] Patch aplicado em {path}")
    return True


def clean_gradle_cache(base_dir: str):
    """Remove caches do módulo app para forçar re-resolução das dependências."""
    targets = [
        os.path.join(base_dir, "app", "build"),
        os.path.join(base_dir, "build"),
    ]
    for t in targets:
        if os.path.isdir(t):
            shutil.rmtree(t, ignore_errors=True)
            print(f"[+] Cache removido: {t}")


def main():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    base_dir = os.path.abspath(base_dir)

    print(f"[i] Repositório alvo: {base_dir}")

    try:
        gradle_file = find_app_build_gradle(base_dir)
    except FileNotFoundError as e:
        print(f"[!] Erro: {e}")
        sys.exit(1)

    changed = patch(gradle_file)

    if changed:
        clean_gradle_cache(base_dir)

    print()
    print("=" * 60)
    print("Concluído. Agora rode no Termux, dentro da pasta do projeto:")
    print()
    print("  ./gradlew clean assembleDebug")
    print()
    print("Se o erro de duplicate class persistir, rode com --info para")
    print("ver qual dependência ainda está trazendo a versão antiga:")
    print()
    print("  ./gradlew assembleDebug --info | grep -i kotlin-stdlib")
    print("=" * 60)


if __name__ == "__main__":
    main()
