#!/usr/bin/env python3
"""
fix_orphaned_case.py

Corrige o erro:
  MusicPicker.java:718: error: orphaned case
      case R.id.cancelButton:

Causa: bug no script anterior (fix_compile_errors.py). A conversão
automática de switch(v.getId()) para if/else if usava uma regex que
não soube lidar com um `case` cujo corpo tinha um bloco `{ }`
aninhado (o `if (mSelectedId >= 0) { ... }` dentro do case
okayButton). Isso cortou a captura no meio, deixando o segundo case
(cancelButton) órfão, fora de qualquer switch.

Este script substitui o método onClick(View v) inteiro em
MusicPicker.java, e também limpa a indentação equivalente em
MusicBrowserActivity.java (que não tinha o bug, mas ficou com
indentação inconsistente do primeiro patch).

Backups (.bak2) são criados antes de qualquer alteração.
Idempotente: rodar de novo não duplica nem quebra nada.

Uso (dentro do Termux, na pasta do projeto Music):
  python fix_orphaned_case.py
ou apontando o caminho do repo:
  python fix_orphaned_case.py /caminho/para/Music
"""

import sys
import os
import shutil

PKG_REL = os.path.join("com", "android", "music")

OLD_MUSICPICKER_BLOCK = '''    public void onClick(View v) {
                int __clickedId = v.getId();
        if (__clickedId == R.id.okayButton) {
    if (mSelectedId >= 0) {
                        setResult(RESULT_OK, new Intent().setData(mSelectedUri));
                        finish();
        }
                break;

            case R.id.cancelButton:
                finish();
                break;
        }
    }
}'''

NEW_MUSICPICKER_BLOCK = '''    public void onClick(View v) {
        int __clickedId = v.getId();
        if (__clickedId == R.id.okayButton) {
            if (mSelectedId >= 0) {
                setResult(RESULT_OK, new Intent().setData(mSelectedUri));
                finish();
            }
        } else if (__clickedId == R.id.cancelButton) {
            finish();
        }
    }
}'''

OLD_BROWSER_BLOCK = '''    public void onClick(View v) {
        Intent intent;
                int __clickedId = v.getId();
        if (__clickedId == R.id.browse_button) {
    intent = new Intent(Intent.ACTION_PICK);
                    intent.setDataAndType(Uri.EMPTY, "vnd.android.cursor.dir/artistalbum");
                    startActivity(intent);
        } else if (__clickedId == R.id.albums_button) {
    intent = new Intent(Intent.ACTION_PICK);
                    intent.setDataAndType(Uri.EMPTY, "vnd.android.cursor.dir/album");
                    startActivity(intent);
        } else if (__clickedId == R.id.tracks_button) {
    intent = new Intent(Intent.ACTION_PICK);
                    intent.setDataAndType(Uri.EMPTY, "vnd.android.cursor.dir/track");
                    startActivity(intent);
        } else if (__clickedId == R.id.playlists_button) {
    intent = new Intent(Intent.ACTION_PICK);
                    intent.setDataAndType(Uri.EMPTY, MediaStore.Audio.Playlists.CONTENT_TYPE);
                    startActivity(intent);
        } else if (__clickedId == R.id.nowplaying) {
    intent = new Intent("com.android.music.PLAYBACK_VIEWER");
                    startActivity(intent);
        }
    }'''

NEW_BROWSER_BLOCK = '''    public void onClick(View v) {
        Intent intent;
        int __clickedId = v.getId();
        if (__clickedId == R.id.browse_button) {
            intent = new Intent(Intent.ACTION_PICK);
            intent.setDataAndType(Uri.EMPTY, "vnd.android.cursor.dir/artistalbum");
            startActivity(intent);
        } else if (__clickedId == R.id.albums_button) {
            intent = new Intent(Intent.ACTION_PICK);
            intent.setDataAndType(Uri.EMPTY, "vnd.android.cursor.dir/album");
            startActivity(intent);
        } else if (__clickedId == R.id.tracks_button) {
            intent = new Intent(Intent.ACTION_PICK);
            intent.setDataAndType(Uri.EMPTY, "vnd.android.cursor.dir/track");
            startActivity(intent);
        } else if (__clickedId == R.id.playlists_button) {
            intent = new Intent(Intent.ACTION_PICK);
            intent.setDataAndType(Uri.EMPTY, MediaStore.Audio.Playlists.CONTENT_TYPE);
            startActivity(intent);
        } else if (__clickedId == R.id.nowplaying) {
            intent = new Intent("com.android.music.PLAYBACK_VIEWER");
            startActivity(intent);
        }
    }'''


def backup(path):
    bak = path + ".bak2"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print(f"[+] Backup criado: {bak}")


def apply_fix(path, old_block, new_block, label):
    if not os.path.isfile(path):
        print(f"[!] Não encontrei {path}. Pulando.")
        return False

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if new_block in content:
        print(f"[=] {label} já está corrigido.")
        return False

    if old_block not in content:
        print(f"[!] Não encontrei o bloco esperado em {label}. "
              f"O arquivo pode já ter sido editado manualmente — revise à mão.")
        return False

    backup(path)
    content = content.replace(old_block, new_block)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[+] {label} corrigido.")
    return True


def main():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    base_dir = os.path.abspath(base_dir)
    print(f"[i] Repositório alvo: {base_dir}\n")

    picker_path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "MusicPicker.java")
    browser_path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "MusicBrowserActivity.java")

    changed = False
    changed |= apply_fix(picker_path, OLD_MUSICPICKER_BLOCK, NEW_MUSICPICKER_BLOCK, "MusicPicker.java")
    changed |= apply_fix(browser_path, OLD_BROWSER_BLOCK, NEW_BROWSER_BLOCK, "MusicBrowserActivity.java")

    print()
    print("=" * 60)
    if changed:
        print("Correção aplicada. Agora rode:")
        print()
        print("  ./gradlew clean assembleDebug")
    else:
        print("Nada para corrigir (já estava tudo aplicado, ou os arquivos "
              "foram editados manualmente e precisam de revisão à mão).")
    print("=" * 60)


if __name__ == "__main__":
    main()
