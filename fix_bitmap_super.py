#!/usr/bin/env python3
"""
fix_bitmap_super.py

Corrige dois bugs deixados pelos patches anteriores:

  1. MusicUtils.java:1050
     error: incompatible types: Bitmap cannot be converted to byte[]

     Causa: o patch anterior (fix_compile_errors.py) tentou decodificar
     o retorno de MediaMetadataRetriever.getEmbeddedPicture() (que é
     byte[]) direto para Bitmap e guardar na variável `art` -- mas
     `art` já era declarada como `byte[] art` no código original do
     AOSP, e é usada como bytes mais adiante no mesmo método (fallback
     para AlbumArt.jpg e decodificação final com BitmapFactory.Options
     para redimensionar). Corrigido para apenas atribuir os bytes
     brutos a `art`, preservando o fluxo original do método.

  2. TouchInterceptor.java:65
     error: call to super must be first statement in constructor

     Causa: o patch anterior inseriu `mContext = context;` ANTES de
     `super(context, attrs);` no construtor -- ilegal em Java, o
     super() sempre precisa ser a primeira instrução. Corrigido
     invertendo a ordem.

Faz backup (.bak3) antes de editar. Idempotente.

Uso (dentro do Termux, na pasta do projeto Music):
  python fix_bitmap_super.py
ou apontando o caminho do repo:
  python fix_bitmap_super.py /caminho/para/Music
"""

import sys
import os
import shutil

PKG_REL = os.path.join("com", "android", "music")

OLD_MUSICUTILS_BLOCK = '''            if (uri != null) {
                MediaMetadataRetriever retriever = new MediaMetadataRetriever();
                try {
                    retriever.setDataSource(context, uri);
                    byte[] artBytes = retriever.getEmbeddedPicture();
                    if (artBytes != null) {
                        art = BitmapFactory.decodeByteArray(artBytes, 0, artBytes.length);
                    }
                } catch (IllegalArgumentException ex) {
                } catch (RuntimeException ex) {
                } finally {
                    try {
                        retriever.release();
                    } catch (RuntimeException ex) {
                    }
                }
            }'''

NEW_MUSICUTILS_BLOCK = '''            if (uri != null) {
                MediaMetadataRetriever retriever = new MediaMetadataRetriever();
                try {
                    retriever.setDataSource(context, uri);
                    art = retriever.getEmbeddedPicture();
                } catch (IllegalArgumentException ex) {
                } catch (RuntimeException ex) {
                } finally {
                    try {
                        retriever.release();
                    } catch (RuntimeException ex) {
                    }
                }
            }'''

OLD_TOUCH_BLOCK = '''    public TouchInterceptor(Context context, AttributeSet attrs) {
        mContext = context;
        super(context, attrs);
        SharedPreferences pref = context.getSharedPreferences("Music", 3);'''

NEW_TOUCH_BLOCK = '''    public TouchInterceptor(Context context, AttributeSet attrs) {
        super(context, attrs);
        mContext = context;
        SharedPreferences pref = context.getSharedPreferences("Music", 3);'''


def backup(path):
    bak = path + ".bak3"
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

    musicutils_path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "MusicUtils.java")
    touch_path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "TouchInterceptor.java")

    changed = False
    changed |= apply_fix(musicutils_path, OLD_MUSICUTILS_BLOCK, NEW_MUSICUTILS_BLOCK, "MusicUtils.java")
    changed |= apply_fix(touch_path, OLD_TOUCH_BLOCK, NEW_TOUCH_BLOCK, "TouchInterceptor.java")

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
