#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_tema_e_notificacao_antiga.py  --  rode na RAIZ do repo, DEPOIS do
fix_remove_androidx.py.

    python3 fix_tema_e_notificacao_antiga.py            # aplica
    python3 fix_tema_e_notificacao_antiga.py --dry-run  # só mostra

1. Tema: o <application> não declarava tema nenhum, então no Android 14
   (targetSdk 34) o app herda o tema padrão claro do sistema. Aqui fixamos
   android:theme="@android:style/Theme", o tema escuro original do Android 1.6
   (as telas que já tinham Theme.NoTitleBar / Theme.Dialog continuam como são,
   porque ambos derivam desse mesmo tema).

2. Notificação abaixo da API 11 (onde não existe Notification.Builder): usa o
   modelo ORIGINAL do Music 1.6 - RemoteViews com R.layout.statusbar, ícone
   stat_notify_musicplayer, sem botões, e a notificação some ao pausar (como o
   gotoIdleState() original). Na API 4 (sem startForeground) a notificação é
   postada direto pelo NotificationManager, como no 1.6.
   Da API 11 em diante continua a notificação nova (MediaStyle + botões).

Idempotente. Sem arquivos .bak (use git diff / git checkout -- <arquivo>).
"""
import os
import re
import sys

DRY = "--dry-run" in sys.argv
ROOT = os.getcwd()
MANIFEST = os.path.join(ROOT, "app", "src", "main", "AndroidManifest.xml")
SERVICE = os.path.join(ROOT, "app", "src", "main", "java", "com", "android",
                       "music", "MediaPlaybackService.java")

changed, skipped, problems = [], [], []


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    if not DRY:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)


def rel(p):
    return os.path.relpath(p, ROOT)


def finish(path, old, new, label):
    if new == old:
        skipped.append("%s (%s: já estava ok)" % (rel(path), label))
    else:
        write(path, new)
        changed.append("%s (%s)" % (rel(path), label))


def match_brace(src, open_idx):
    depth, i, n = 0, open_idx, len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
            continue
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in "\"'":
            q = c
            i += 1
            while i < n and src[i] != q:
                if src[i] == "\\":
                    i += 1
                i += 1
            i += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def replace_method(src, name, new_text):
    pat = re.compile(r"^[ \t]*(?:public|private|protected)[^\n;{}=]*?\b" + re.escape(name)
                     + r"\s*\([^)]*\)\s*\{", re.M)
    m = pat.search(src)
    if not m:
        return src, False
    end = match_brace(src, m.end() - 1)
    if end < 0:
        return src, False
    return src[:m.start()] + new_text.rstrip("\n") + src[end + 1:], True


# ---------------------------------------------------------------------------
# 1. tema escuro do Android 1.6
# ---------------------------------------------------------------------------
def patch_theme():
    if not os.path.isfile(MANIFEST):
        problems.append("não achei %s" % rel(MANIFEST))
        return
    old = read(MANIFEST)
    m = re.search(r"<application\b[^>]*>", old, re.S)
    if not m:
        problems.append("tag <application> não encontrada no manifest")
        return
    tag = m.group(0)
    if re.search(r"android:theme\s*=", tag):
        if '"@android:style/Theme"' in tag:
            skipped.append("%s (tema: já estava ok)" % rel(MANIFEST))
        else:
            problems.append("o <application> já tem outro android:theme; "
                            "troque você mesmo para @android:style/Theme")
        return
    new_tag = tag.replace("<application", '<application android:theme="@android:style/Theme"', 1)
    new = old[:m.start()] + new_tag + old[m.end():]
    finish(MANIFEST, old, new, "android:theme=@android:style/Theme")


# ---------------------------------------------------------------------------
# 2. notificação antiga (abaixo da API 11)
# ---------------------------------------------------------------------------
M_LEGACY = r'''    /**
     * Notificação do Music original (Android 1.6): RemoteViews com
     * R.layout.statusbar, sem botões. Usada só abaixo da API 11.
     */
    @SuppressWarnings("deprecation")
    private Notification buildLegacyNotification() {
        RemoteViews views = new RemoteViews(getPackageName(), R.layout.statusbar);
        views.setImageViewResource(R.id.icon, R.drawable.stat_notify_musicplayer);
        if (getAudioId() < 0) {
            // streaming
            views.setTextViewText(R.id.trackname, getPath());
            views.setTextViewText(R.id.artistalbum, null);
        } else {
            String artist = getArtistName();
            views.setTextViewText(R.id.trackname, getTrackName());
            if (artist == null || artist.equals(MediaFileCompat.UNKNOWN_STRING)) {
                artist = getString(R.string.unknown_artist_name);
            }
            String album = getAlbumName();
            if (album == null || album.equals(MediaFileCompat.UNKNOWN_STRING)) {
                album = getString(R.string.unknown_album_name);
            }
            views.setTextViewText(R.id.artistalbum,
                    getString(R.string.notification_artist_album, artist, album));
        }

        Notification status = new Notification();
        status.contentView = views;
        status.flags |= Notification.FLAG_ONGOING_EVENT;
        status.icon = R.drawable.stat_notify_musicplayer;
        status.contentIntent = PendingIntent.getActivity(this, 0,
                new Intent("com.android.music.PLAYBACK_VIEWER"), 0);
        return status;
    }'''

M_START_FG = r'''    private void startForegroundCompat() {
        Notification n = buildNotification();
        if (n == null) {
            return;
        }
        if (Build.VERSION.SDK_INT >= 5) {
            startForeground(PLAYBACKSERVICE_STATUS, n);
        } else if (mNotificationManager != null) {
            // API 4 (Android 1.6) não tem startForeground(): só posta a notificação.
            mNotificationManager.notify(PLAYBACKSERVICE_STATUS, n);
        }
    }'''

M_NOTIFY = r'''    private void notifyCompat() {
        if (mNotificationManager == null) {
            return;
        }
        if (Build.VERSION.SDK_INT < 11) {
            // Modelo do Android 1.6: ao pausar, a notificação some.
            mNotificationManager.cancel(PLAYBACKSERVICE_STATUS);
            return;
        }
        Notification n = buildNotification();
        if (n != null) {
            mNotificationManager.notify(PLAYBACKSERVICE_STATUS, n);
        }
    }'''


def patch_service():
    if not os.path.isfile(SERVICE):
        problems.append("não achei %s" % rel(SERVICE))
        return
    old = read(SERVICE)
    src = old

    if "private void startForegroundCompat()" not in src:
        problems.append("rode primeiro o fix_remove_androidx.py "
                        "(MediaPlaybackService ainda não foi migrado)")
        return
    if "private Notification buildLegacyNotification()" in src:
        skipped.append("%s (notificação antiga: já estava ok)" % rel(SERVICE))
        return

    # import do RemoteViews
    if "import android.widget.RemoteViews;" not in src:
        anchor = "import android.widget.Toast;"
        if anchor in src:
            src = src.replace(anchor, "import android.widget.RemoteViews;\n" + anchor, 1)
        else:
            problems.append("não achei a âncora de imports (android.widget.Toast)")
            return

    # abaixo da API 11: em vez de null, usa a notificação do 1.6
    pat = re.compile(r"if \(Build\.VERSION\.SDK_INT < 11\) \{\s*return null;\s*\}")
    if not pat.search(src):
        problems.append("não achei o bloco 'SDK_INT < 11 -> return null' em buildNotification")
        return
    src = pat.sub("if (Build.VERSION.SDK_INT < 11) {\n            return buildLegacyNotification();\n        }",
                  src, count=1)
    src = src.replace("// Abaixo disso o service toca sem notificação.",
                      "// Abaixo disso usa o modelo original do Android 1.6 (RemoteViews, sem botões).")

    # método novo, logo depois de buildNotification()
    m = re.search(r"private Notification buildNotification\(\)\s*\{", src)
    if not m:
        problems.append("não achei buildNotification()")
        return
    end = match_brace(src, m.end() - 1)
    src = src[:end + 1] + "\n\n" + M_LEGACY + src[end + 1:]

    # startForegroundCompat / notifyCompat
    for name, text in (("startForegroundCompat", M_START_FG), ("notifyCompat", M_NOTIFY)):
        src, ok = replace_method(src, name, text)
        if not ok:
            problems.append("método %s não encontrado" % name)

    finish(SERVICE, old, src, "notificação do Android 1.6 abaixo da API 11")


def main():
    if not os.path.isfile(os.path.join(ROOT, "settings.gradle")) or \
            not os.path.isdir(os.path.join(ROOT, "app")):
        print("ERRO: rode na raiz do repo (onde ficam settings.gradle e a pasta app/).")
        return 2

    print("== fix_tema_e_notificacao_antiga %s==" % ("(dry-run) " if DRY else ""))
    if not os.path.isfile(SERVICE) or \
            "private void startForegroundCompat()" not in read(SERVICE):
        print("ERRO: rode primeiro o fix_remove_androidx.py (nada foi alterado).")
        return 1
    patch_theme()
    patch_service()

    print("\nAlterados:")
    for c in changed or ["(nada)"]:
        print("  + " + c if c != "(nada)" else "  (nada)")
    print("\nJá ok / ignorados:")
    for s in skipped:
        print("  = " + s)
    if problems:
        print("\nPROBLEMAS:")
        for p in problems:
            print("  ! " + p)
        return 1
    print("\nOK. Agora rode:  gradle clean assembleDebug")
    return 0


if __name__ == "__main__":
    sys.exit(main())
