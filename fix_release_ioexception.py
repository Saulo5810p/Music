#!/usr/bin/env python3
"""
fix_release_ioexception.py

Corrige o erro:
  MusicUtils.java:1053: error: unreported exception IOException;
  must be caught or declared to be thrown
      retriever.release();

Causa: MediaMetadataRetriever.release() declara `throws IOException`
(checked exception). O patch anterior (fix_bitmap_super.py /
fix_compile_errors.py) só capturava RuntimeException ao redor dela,
então o compilador exige que a IOException também seja tratada.

Correção: adiciona `catch (IOException ex) {}` antes do catch de
RuntimeException já existente. IOException já está importado no
arquivo (usado em outros pontos do mesmo método).

Faz backup (.bak4) antes de editar. Idempotente.

Uso (dentro do Termux, na pasta do projeto Music):
  python fix_release_ioexception.py
ou apontando o caminho do repo:
  python fix_release_ioexception.py /caminho/para/Music
"""

import sys
import os
import shutil

PKG_REL = os.path.join("com", "android", "music")

OLD_BLOCK = '''                } finally {
                    try {
                        retriever.release();
                    } catch (RuntimeException ex) {
                    }
                }'''

NEW_BLOCK = '''                } finally {
                    try {
                        retriever.release();
                    } catch (IOException ex) {
                    } catch (RuntimeException ex) {
                    }
                }'''


def backup(path):
    bak = path + ".bak4"
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

    path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "MusicUtils.java")
    changed = apply_fix(path, OLD_BLOCK, NEW_BLOCK, "MusicUtils.java")

    print()
    print("=" * 60)
    if changed:
        print("Correção aplicada. Agora rode:")
        print()
        print("  ./gradlew clean assembleDebug")
    else:
        print("Nada para corrigir (já estava tudo aplicado, ou o arquivo "
              "foi editado manualmente e precisa de revisão à mão).")
    print("=" * 60)


if __name__ == "__main__":
    main()
