#!/usr/bin/env python3
"""
fix_phone_state_permission.py

Corrige o crash:
  FATAL EXCEPTION: main
  ... Unable to create service com.android.music.MediaPlaybackService:
  java.lang.SecurityException: listen
  ...
  at com.android.music.MediaPlaybackService.onCreate(MediaPlaybackService.java:335)

Causa: MediaPlaybackService.onCreate() chama
TelephonyManager.listen(mPhoneStateListener, LISTEN_CALL_STATE) para
pausar a música automaticamente durante ligações (funcionalidade
original do Donut). Isso exige a permissão READ_PHONE_STATE, que
tinha sido removida do AndroidManifest.xml numa limpeza anterior de
permissões antigas incompatíveis.

Decisão (confirmada com o usuário): manter a funcionalidade,
restaurando READ_PHONE_STATE e adicionando o runtime request
obrigatório desde Android 6.0 (API 23), no mesmo padrão que já
existe no projeto para POST_NOTIFICATIONS (Android 13+).

O script:
  1. Adiciona <uses-permission android:name="android.permission.
     READ_PHONE_STATE" /> ao AndroidManifest.xml, se ainda não
     existir.
  2. Em MusicBrowserActivity.java, adiciona um método
     requestPhoneStatePermissionIfNeeded() seguindo exatamente o
     estilo do requestNotificationPermissionIfNeeded() já existente,
     e chama esse método a partir de onCreate().

Faz backup (.bak6) dos dois arquivos antes de editar. Idempotente.

Uso (dentro do Termux, na pasta do projeto Music):
  python fix_phone_state_permission.py
ou apontando o caminho do repo:
  python fix_phone_state_permission.py /caminho/para/Music
"""

import sys
import os
import shutil

PKG_REL = os.path.join("com", "android", "music")

MANIFEST_PERMISSION_LINE = (
    '    <uses-permission android:name="android.permission.READ_PHONE_STATE" />\n'
)

MANIFEST_ANCHOR = (
    '    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />\n'
)

OLD_ONCREATE_CALL = "        requestNotificationPermissionIfNeeded();\n        init();"
NEW_ONCREATE_CALL = (
    "        requestNotificationPermissionIfNeeded();\n"
    "        requestPhoneStatePermissionIfNeeded();\n"
    "        init();"
)

OLD_METHOD_ANCHOR = '''    private void requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1);
            }
        }
    }'''

NEW_METHOD_BLOCK = OLD_METHOD_ANCHOR + '''

    /**
     * MediaPlaybackService listens for phone call state (to pause
     * playback during calls), which requires the runtime
     * READ_PHONE_STATE permission since Android 6.0 (API 23).
     */
    private void requestPhoneStatePermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.READ_PHONE_STATE)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.READ_PHONE_STATE}, 2);
            }
        }
    }'''


def backup(path):
    bak = path + ".bak6"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print(f"[+] Backup criado: {bak}")


def fix_manifest(base_dir):
    path = os.path.join(base_dir, "app", "src", "main", "AndroidManifest.xml")
    if not os.path.isfile(path):
        print(f"[!] Não encontrei {path}. Pulando.")
        return False

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "android.permission.READ_PHONE_STATE" in content:
        print("[=] AndroidManifest.xml já tem READ_PHONE_STATE.")
        return False

    if MANIFEST_ANCHOR not in content:
        print("[!] Não encontrei o ponto de referência (POST_NOTIFICATIONS) no "
              "manifest. Adicione manualmente:")
        print(f"    {MANIFEST_PERMISSION_LINE.strip()}")
        return False

    backup(path)
    content = content.replace(MANIFEST_ANCHOR, MANIFEST_ANCHOR + MANIFEST_PERMISSION_LINE)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[+] READ_PHONE_STATE adicionado ao AndroidManifest.xml")
    return True


def fix_activity(base_dir):
    path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "MusicBrowserActivity.java")
    if not os.path.isfile(path):
        print(f"[!] Não encontrei {path}. Pulando.")
        return False

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "requestPhoneStatePermissionIfNeeded" in content:
        print("[=] MusicBrowserActivity.java já tem requestPhoneStatePermissionIfNeeded().")
        return False

    if OLD_ONCREATE_CALL not in content:
        print("[!] Não encontrei o ponto de chamada esperado em onCreate(). "
              "Revise manualmente MusicBrowserActivity.java.")
        return False

    if OLD_METHOD_ANCHOR not in content:
        print("[!] Não encontrei o método requestNotificationPermissionIfNeeded() "
              "no formato esperado. Revise manualmente.")
        return False

    backup(path)
    content = content.replace(OLD_ONCREATE_CALL, NEW_ONCREATE_CALL)
    content = content.replace(OLD_METHOD_ANCHOR, NEW_METHOD_BLOCK)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[+] requestPhoneStatePermissionIfNeeded() adicionado e chamado em onCreate().")
    return True


def main():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    base_dir = os.path.abspath(base_dir)
    print(f"[i] Repositório alvo: {base_dir}\n")

    changed = False
    changed |= fix_manifest(base_dir)
    changed |= fix_activity(base_dir)

    print()
    print("=" * 60)
    if changed:
        print("Correções aplicadas. Agora rode:")
        print()
        print("  ./gradlew clean assembleDebug")
        print()
        print("Na primeira execução após instalar, o Android vai pedir as")
        print("permissões READ_PHONE_STATE e POST_NOTIFICATIONS -- conceda-as")
        print("para o recurso de pausar durante ligações funcionar.")
    else:
        print("Nada para corrigir (já estava tudo aplicado).")
    print("=" * 60)


if __name__ == "__main__":
    main()
