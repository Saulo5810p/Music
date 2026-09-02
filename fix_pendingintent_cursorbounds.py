#!/usr/bin/env python3
"""
fix_pendingintent_cursorbounds.py

Corrige os 2 crashes reportados após navegar/tocar música:

  1. IllegalArgumentException: ...requires that one of FLAG_IMMUTABLE
     or FLAG_MUTABLE be specified when creating a PendingIntent
     (MediaAppWidgetProvider.linkButtons)

     Causa: desde Android 12 (S, API 31), todo PendingIntent precisa
     declarar FLAG_IMMUTABLE ou FLAG_MUTABLE. O widget provider (código
     original do Donut, nunca tocado) passava "0 /* no flags */" nos
     4 PendingIntent que cria. Nenhum deles precisa ser mutável (não
     usam inline replies nem bubbles), então FLAG_IMMUTABLE é a
     escolha correta nos 4 pontos.

     Os PendingIntent da notificação em MediaPlaybackService.java já
     tinham FLAG_IMMUTABLE corretamente -- não precisam de correção.

  2. CursorIndexOutOfBoundsException: Index 0 requested, with a size
     of 0 (PlaylistBrowserActivity.mergedCursor, ao abrir a aba de
     playlists)

     Causa: bug introduzido por um patch anterior deste mesmo projeto
     (fix_runtime_crashes.py), que trocou a projeção "count(*)" por
     MediaStore.Audio.Media._ID para contornar a incompatibilidade
     dessa função SQL com o MediaStore moderno -- mas esqueceu de
     também trocar a leitura do resultado. Com "count(*)" a query
     sempre retornava exatamente 1 linha (o total agregado), lida com
     counter.moveToFirst(); counter.getInt(0). Com _ID like projeção,
     a query agora retorna 1 linha POR PODCAST -- 0 linhas quando não
     há nenhum, o que faz moveToFirst() falhar. A leitura correta,
     coerente com o resto do código já corrigido, é counter.getCount().

Faz backup (.bak8) de cada arquivo antes de editar. Idempotente.

Uso (dentro do Termux, na pasta do projeto Music):
  python fix_pendingintent_cursorbounds.py
ou apontando o caminho do repo:
  python fix_pendingintent_cursorbounds.py /caminho/para/Music
"""

import sys
import os
import shutil

PKG_REL = os.path.join("com", "android", "music")


def backup(path):
    bak = path + ".bak8"
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


# ---------------------------------------------------------------------
# 1. MediaAppWidgetProvider: PendingIntent sem FLAG_IMMUTABLE
# ---------------------------------------------------------------------
WIDGET_OLD = '''        if (playerActive) {
            intent = new Intent(context, MediaPlaybackActivity.class);
            pendingIntent = PendingIntent.getActivity(context,
                    0 /* no requestCode */, intent, 0 /* no flags */);
            views.setOnClickPendingIntent(R.id.album_appwidget, pendingIntent);
        } else {
            intent = new Intent(context, MusicBrowserActivity.class);
            pendingIntent = PendingIntent.getActivity(context,
                    0 /* no requestCode */, intent, 0 /* no flags */);
            views.setOnClickPendingIntent(R.id.album_appwidget, pendingIntent);
        }
        
        intent = new Intent(MediaPlaybackService.TOGGLEPAUSE_ACTION);
        intent.setComponent(serviceName);
        pendingIntent = PendingIntent.getService(context,
                0 /* no requestCode */, intent, 0 /* no flags */);
        views.setOnClickPendingIntent(R.id.control_play, pendingIntent);
        
        intent = new Intent(MediaPlaybackService.NEXT_ACTION);
        intent.setComponent(serviceName);
        pendingIntent = PendingIntent.getService(context,
                0 /* no requestCode */, intent, 0 /* no flags */);
        views.setOnClickPendingIntent(R.id.control_next, pendingIntent);'''

WIDGET_NEW = '''        if (playerActive) {
            intent = new Intent(context, MediaPlaybackActivity.class);
            pendingIntent = PendingIntent.getActivity(context,
                    0 /* no requestCode */, intent, PendingIntent.FLAG_IMMUTABLE);
            views.setOnClickPendingIntent(R.id.album_appwidget, pendingIntent);
        } else {
            intent = new Intent(context, MusicBrowserActivity.class);
            pendingIntent = PendingIntent.getActivity(context,
                    0 /* no requestCode */, intent, PendingIntent.FLAG_IMMUTABLE);
            views.setOnClickPendingIntent(R.id.album_appwidget, pendingIntent);
        }
        
        intent = new Intent(MediaPlaybackService.TOGGLEPAUSE_ACTION);
        intent.setComponent(serviceName);
        pendingIntent = PendingIntent.getService(context,
                0 /* no requestCode */, intent, PendingIntent.FLAG_IMMUTABLE);
        views.setOnClickPendingIntent(R.id.control_play, pendingIntent);
        
        intent = new Intent(MediaPlaybackService.NEXT_ACTION);
        intent.setComponent(serviceName);
        pendingIntent = PendingIntent.getService(context,
                0 /* no requestCode */, intent, PendingIntent.FLAG_IMMUTABLE);
        views.setOnClickPendingIntent(R.id.control_next, pendingIntent);'''

# ---------------------------------------------------------------------
# 2. PlaylistBrowserActivity: CursorIndexOutOfBounds em mergedCursor
# ---------------------------------------------------------------------
PBA_OLD = '''        // check if there are any podcasts
        Cursor counter = MusicUtils.query(this, MediaStore.Audio.Media.EXTERNAL_CONTENT_URI,
                new String[] {MediaStore.Audio.Media._ID}, "is_podcast=1", null, null);
        if (counter != null) {
            counter.moveToFirst();
            int numpodcasts = counter.getInt(0);
            counter.close();
            if (numpodcasts > 0) {'''

PBA_NEW = '''        // check if there are any podcasts
        Cursor counter = MusicUtils.query(this, MediaStore.Audio.Media.EXTERNAL_CONTENT_URI,
                new String[] {MediaStore.Audio.Media._ID}, "is_podcast=1", null, null);
        if (counter != null) {
            int numpodcasts = counter.getCount();
            counter.close();
            if (numpodcasts > 0) {'''


def main():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    base_dir = os.path.abspath(base_dir)
    print(f"[i] Repositório alvo: {base_dir}\n")

    widget_path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "MediaAppWidgetProvider.java")
    pba_path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "PlaylistBrowserActivity.java")

    changed = False
    print("--- 1/2: MediaAppWidgetProvider — PendingIntent sem flag ---")
    changed |= apply_fix(widget_path, WIDGET_OLD, WIDGET_NEW, "MediaAppWidgetProvider.java")

    print("\n--- 2/2: PlaylistBrowserActivity — CursorIndexOutOfBounds ---")
    changed |= apply_fix(pba_path, PBA_OLD, PBA_NEW, "PlaylistBrowserActivity.java")

    print()
    print("=" * 60)
    if changed:
        print("Correções aplicadas. Agora rode:")
        print()
        print("  ./gradlew clean assembleDebug")
        print()
        print("Teste: tocar uma música (deve iniciar a reprodução) e abrir")
        print("a aba de playlists (não deve mais crashar).")
    else:
        print("Nada para corrigir (já estava tudo aplicado).")
    print("=" * 60)


if __name__ == "__main__":
    main()
