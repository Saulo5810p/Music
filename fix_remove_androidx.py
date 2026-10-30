#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_remove_androidx.py  --  rode na RAIZ do repo (a pasta que tem settings.gradle).

    python3 fix_remove_androidx.py            # aplica
    python3 fix_remove_androidx.py --dry-run  # só mostra o que mudaria

O que faz (Java puro, minSdk 4 mantido, zero androidx):

  1. app/build.gradle      remove androidx.media / androidx.core e o bloco
                           do fix_kotlin_duplicate (não há mais Kotlin nenhum).
                           Essa era a causa do erro "minSdkVersion 4 cannot be
                           smaller than version 19 declared in library
                           [androidx.media:media:1.7.0]".
  2. gradle.properties     remove android.useAndroidX / enableJetifier.
  3. proguard-rules.pro    remove as regras de androidx / support.v4.
  4. MediaPlaybackService  troca MediaSessionCompat, NotificationCompat,
                           NotificationManagerCompat, NotificationChannelCompat,
                           MediaButtonReceiver e MediaStyle do androidx pelas
                           classes do próprio framework (MediaSession,
                           Notification.Builder, NotificationChannel...), sempre
                           protegidas por Build.VERSION.SDK_INT, então o app
                           continua carregando em API antiga (minSdk 4).
                           Também protege stopForeground(int) (API 24) e
                           checkSelfPermission (API 23).
  5. MusicBrowserActivity  ActivityCompat -> métodos do próprio Activity
                           (já estavam dentro de if SDK_INT >= M / TIRAMISU).
  6. MediaButtonIntentReceiver
                           ContextCompat.startForegroundService -> helper local.
  7. values*/strings.xml   rename_playlist_diff_prompt ganha formatted="false"
                           (some com os avisos de "non-positional format").

O script é idempotente: rodar duas vezes não estraga nada.
Não cria arquivos .bak (use `git diff` / `git checkout -- <arquivo>`).
"""
import os
import re
import sys

DRY = "--dry-run" in sys.argv
ROOT = os.getcwd()
JAVA_DIR = os.path.join(ROOT, "app", "src", "main", "java", "com", "android", "music")
RES_DIR = os.path.join(ROOT, "app", "src", "main", "res")

changed = []
skipped = []
problems = []


# ----------------------------------------------------------------------------
# utilidades
# ----------------------------------------------------------------------------
def read(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    if DRY:
        return
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def rel(path):
    return os.path.relpath(path, ROOT)


def finish(path, old, new, label):
    """Grava se mudou e registra o resultado."""
    if new == old:
        skipped.append("%s (%s: já estava ok)" % (rel(path), label))
        return
    write(path, new)
    changed.append("%s (%s)" % (rel(path), label))


def require(path):
    if not os.path.isfile(path):
        problems.append("arquivo não encontrado: %s" % rel(path))
        return False
    return True


def match_brace(src, open_idx):
    """Dado o índice de um '{', devolve o índice do '}' correspondente,
    ignorando chaves dentro de strings, chars e comentários."""
    depth = 0
    i = open_idx
    n = len(src)
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
        if c == '"' or c == "'":
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
    """Substitui o método `name` inteiro (assinatura + corpo)."""
    pat = re.compile(
        r"^[ \t]*(?:public|private|protected)[^\n;{}=]*?\b" + re.escape(name)
        + r"\s*\([^)]*\)\s*(?:throws[^{]+)?\{", re.M)
    m = pat.search(src)
    if not m:
        return src, False
    end = match_brace(src, m.end() - 1)
    if end < 0:
        return src, False
    return src[:m.start()] + new_text.rstrip("\n") + src[end + 1:], True


# ----------------------------------------------------------------------------
# 1. app/build.gradle
# ----------------------------------------------------------------------------
def patch_app_gradle():
    path = os.path.join(ROOT, "app", "build.gradle")
    if not require(path):
        return
    old = read(path)
    new = old

    new = re.sub(r"^[ \t]*(?:implementation|api|compileOnly)\s*\(?\s*['\"]"
                 r"(?:androidx|com\.android\.support)[^'\"]*['\"]\s*\)?[ \t]*\n",
                 "", new, flags=re.M)

    new = re.sub(r"\n?// >>> fix_kotlin_duplicate\.py.*?// <<< fix_kotlin_duplicate\.py[ \t]*\n?",
                 "\n", new, flags=re.S)

    # dependencies {} ficou vazio? deixa só um comentário
    new = re.sub(r"dependencies\s*\{\s*\}",
                 "dependencies {\n    // Sem dependências: Java puro, só o framework do Android.\n}", new)

    new = new.rstrip("\n") + "\n"
    finish(path, old, new, "sem androidx")

    m = re.search(r"minSdk(?:Version)?\s*=?\s*(\d+)", new)
    if not m or m.group(1) != "4":
        problems.append("atenção: minSdk em app/build.gradle não é 4 (encontrado: %s)"
                        % (m.group(1) if m else "nenhum"))


# ----------------------------------------------------------------------------
# 2. gradle.properties
# ----------------------------------------------------------------------------
def patch_gradle_properties():
    path = os.path.join(ROOT, "gradle.properties")
    if not require(path):
        return
    old = read(path)
    new = re.sub(r"^[ \t]*android\.(?:useAndroidX|enableJetifier)\s*=.*\n?", "", old, flags=re.M)
    finish(path, old, new, "sem useAndroidX")


# ----------------------------------------------------------------------------
# 3. proguard-rules.pro
# ----------------------------------------------------------------------------
PRO_HEADER = """# Regras R8/ProGuard para o port do Music (AOSP Android 1.6 -> moderno).
#
# Java puro, sem androidx: o R8 só precisa preservar o que é acessado por
# nome (componentes do manifest e a interface AIDL).

"""


def patch_proguard():
    path = os.path.join(ROOT, "app", "proguard-rules.pro")
    if not require(path):
        return
    old = read(path)
    lines = old.split("\n")

    def find(prefix):
        for idx, ln in enumerate(lines):
            if ln.startswith(prefix):
                return idx
        return -1

    # blocos de seção do androidx (do "AndroidX Media" até antes de "Parcelable")
    a = find("# --- AndroidX Media")
    b = find("# --- Parcelable")
    if a >= 0 and b > a:
        del lines[a:b]

    # cabeçalho antigo (fala de AndroidX) -> cabeçalho novo
    c = find("# --- Componentes do proprio app")
    if c > 0 and any("AndroidX" in ln or "androidx" in ln for ln in lines[:c]):
        lines = PRO_HEADER.split("\n")[:-1] + lines[c:]

    # rede de segurança: qualquer regra solta que cite androidx / support
    lines = [ln for ln in lines
             if not re.match(r"^-(keep\w*|dontwarn)\b.*(androidx|android\.support)", ln)]

    new = "\n".join(lines)
    finish(path, old, new, "sem regras androidx")


# ----------------------------------------------------------------------------
# 4. MediaPlaybackService.java
# ----------------------------------------------------------------------------
NEW_IMPORTS = [
    "import android.app.NotificationChannel;",
    "import android.app.NotificationManager;",
    "import android.media.MediaMetadata;",
    "import android.media.session.MediaSession;",
    "import android.media.session.PlaybackState;",
]

M_CREATE_CHANNEL = r'''    private void createNotificationChannel() {
        // NotificationChannel só existe a partir do Android 8 (API 26).
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel channel = new NotificationChannel(
                    NOTIFICATION_CHANNEL_ID,
                    getString(R.string.notification_channel_playback),
                    NotificationManager.IMPORTANCE_LOW);
            channel.setShowBadge(false);
            mNotificationManager.createNotificationChannel(channel);
        }
    }'''

M_SETUP_SESSION = r'''    @SuppressWarnings("deprecation")
    private void setUpMediaSession() {
        // android.media.session.MediaSession só existe a partir do Android 5
        // (API 21). Abaixo disso o app toca normal, só sem a sessão.
        if (Build.VERSION.SDK_INT < 21) {
            return;
        }
        mSession = new MediaSession(this, "MediaPlaybackService");
        mSession.setCallback(new MediaSession.Callback() {
            @Override
            public void onPlay() {
                play();
            }

            @Override
            public void onPause() {
                pause();
            }

            @Override
            public void onSkipToNext() {
                next(true);
            }

            @Override
            public void onSkipToPrevious() {
                prev();
            }

            @Override
            public void onSeekTo(long pos) {
                seek(pos);
                updateMediaSession(PLAYSTATE_CHANGED);
            }

            @Override
            public void onStop() {
                pause();
                seek(0);
            }
        });
        mSession.setFlags(MediaSession.FLAG_HANDLES_MEDIA_BUTTONS |
                MediaSession.FLAG_HANDLES_TRANSPORT_CONTROLS);
        mSession.setActive(true);
    }'''

M_UPDATE_SESSION = r'''    private void updateMediaSession(String what) {
        if (mSession != null) {
            long actions = PlaybackState.ACTION_PLAY_PAUSE |
                    PlaybackState.ACTION_PLAY |
                    PlaybackState.ACTION_PAUSE |
                    PlaybackState.ACTION_SKIP_TO_NEXT |
                    PlaybackState.ACTION_SKIP_TO_PREVIOUS |
                    PlaybackState.ACTION_SEEK_TO |
                    PlaybackState.ACTION_STOP;

            int state = isPlaying() ? PlaybackState.STATE_PLAYING
                    : PlaybackState.STATE_PAUSED;

            PlaybackState playbackState = new PlaybackState.Builder()
                    .setActions(actions)
                    .setState(state, position(), 1.0f)
                    .build();
            mSession.setPlaybackState(playbackState);

            if (!what.equals(PLAYSTATE_CHANGED)) {
                String title;
                String artist;
                String album;
                if (getAudioId() < 0) {
                    title = getPath();
                    artist = null;
                    album = null;
                } else {
                    title = getTrackName();
                    artist = getArtistName();
                    if (artist == null || artist.equals(MediaFileCompat.UNKNOWN_STRING)) {
                        artist = getString(R.string.unknown_artist_name);
                    }
                    album = getAlbumName();
                    if (album == null || album.equals(MediaFileCompat.UNKNOWN_STRING)) {
                        album = getString(R.string.unknown_album_name);
                    }
                }
                Bitmap art = MusicUtils.getArtwork(this, getAlbumId());

                MediaMetadata.Builder metaBuilder = new MediaMetadata.Builder()
                        .putString(MediaMetadata.METADATA_KEY_TITLE, title)
                        .putString(MediaMetadata.METADATA_KEY_ARTIST, artist)
                        .putString(MediaMetadata.METADATA_KEY_ALBUM, album)
                        .putLong(MediaMetadata.METADATA_KEY_DURATION, duration());
                if (art != null) {
                    metaBuilder.putBitmap(MediaMetadata.METADATA_KEY_ALBUM_ART, art);
                }
                mSession.setMetadata(metaBuilder.build());
            }
        }

        if (mIsSupposedToBePlaying) {
            startForegroundCompat();
        } else {
            // Keep the notification visible (paused state) but let the
            // service leave the foreground state, same behavior as
            // before: it's dismissed only from gotoIdleState().
            stopForegroundCompat(false);
            notifyCompat();
        }
    }'''

M_BUILD_NOTIFICATION = r'''    @SuppressWarnings("deprecation")
    private Notification buildNotification() {
        // Notification.Builder só existe a partir do Android 3 (API 11).
        // Abaixo disso o service toca sem notificação.
        if (Build.VERSION.SDK_INT < 11) {
            return null;
        }
        boolean playing = isPlaying();

        PendingIntent contentIntent = PendingIntent.getActivity(this, 0,
                new Intent("com.android.music.PLAYBACK_VIEWER")
                        .setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP),
                pendingFlags());

        String title;
        String artist;
        if (getAudioId() < 0) {
            // streaming a raw URL, no MediaStore metadata available
            title = getPath();
            artist = null;
        } else {
            title = getTrackName();
            artist = getArtistName();
            if (artist == null || artist.equals(MediaFileCompat.UNKNOWN_STRING)) {
                artist = getString(R.string.unknown_artist_name);
            }
        }
        Bitmap art = MusicUtils.getArtwork(this, getAlbumId());

        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= 26) {
            builder = new Notification.Builder(this, NOTIFICATION_CHANNEL_ID);
        } else {
            builder = new Notification.Builder(this);
        }
        builder.setSmallIcon(R.drawable.ic_notif_status_bar)
                .setContentTitle(title)
                .setContentText(artist)
                .setContentIntent(contentIntent)
                .setLargeIcon(art)
                .setOngoing(playing)
                .setOnlyAlertOnce(true);

        if (Build.VERSION.SDK_INT >= 21) {
            builder.setVisibility(Notification.VISIBILITY_PUBLIC);
        }

        // Botões da notificação (API 16+). Cada um manda um comando
        // para o próprio service (ver onStart), sem passar por receiver.
        if (Build.VERSION.SDK_INT >= 16) {
            builder.addAction(R.drawable.ic_notif_previous,
                    getString(R.string.notification_action_previous),
                    commandIntent(1, CMDPREVIOUS));

            builder.addAction(playing ? R.drawable.ic_notif_pause : R.drawable.ic_notif_play,
                    getString(playing ? R.string.notification_action_pause
                                      : R.string.notification_action_play),
                    commandIntent(2, CMDTOGGLEPAUSE));

            builder.addAction(R.drawable.ic_notif_next,
                    getString(R.string.notification_action_next),
                    commandIntent(3, CMDNEXT));

            int repeatIconRes;
            switch (getRepeatMode()) {
                case REPEAT_CURRENT:
                    repeatIconRes = R.drawable.ic_notif_repeat_one;
                    break;
                case REPEAT_ALL:
                    repeatIconRes = R.drawable.ic_notif_repeat_all;
                    break;
                default:
                    repeatIconRes = R.drawable.ic_notif_repeat_none;
                    break;
            }
            builder.addAction(repeatIconRes,
                    getString(R.string.notification_action_repeat),
                    commandIntent(4, CMDCYCLEREPEAT));
        }

        if (Build.VERSION.SDK_INT >= 21 && mSession != null) {
            builder.setStyle(new Notification.MediaStyle()
                    .setMediaSession(mSession.getSessionToken())
                    .setShowActionsInCompactView(0, 1, 2));
        }

        return Build.VERSION.SDK_INT >= 16 ? builder.build() : builder.getNotification();
    }'''

HELPERS = r'''

    // ---- helpers locais com checagem de API (sem bibliotecas compat) -------

    /** FLAG_IMMUTABLE só existe a partir da API 23. */
    private static int pendingFlags() {
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= 23) {
            flags |= PendingIntent.FLAG_IMMUTABLE;
        }
        return flags;
    }

    /** PendingIntent que manda um comando (CMD*) para este próprio service. */
    private PendingIntent commandIntent(int requestCode, String command) {
        Intent i = new Intent(SERVICECMD, null, this, MediaPlaybackService.class);
        i.putExtra(CMDNAME, command);
        return PendingIntent.getService(this, requestCode, i, pendingFlags());
    }

    private void startForegroundCompat() {
        if (Build.VERSION.SDK_INT < 5) {
            return; // startForeground() não existe na API 4
        }
        Notification n = buildNotification();
        if (n != null) {
            startForeground(PLAYBACKSERVICE_STATUS, n);
        }
    }

    private void notifyCompat() {
        Notification n = buildNotification();
        if (n != null && mNotificationManager != null) {
            mNotificationManager.notify(PLAYBACKSERVICE_STATUS, n);
        }
    }

    /** stopForeground(int) só existe na API 24; antes era stopForeground(boolean). */
    private void stopForegroundCompat(boolean removeNotification) {
        if (Build.VERSION.SDK_INT >= 24) {
            stopForeground(removeNotification ? Service.STOP_FOREGROUND_REMOVE
                                              : Service.STOP_FOREGROUND_DETACH);
        } else if (Build.VERSION.SDK_INT >= 5) {
            stopForeground(removeNotification);
        }
    }

    /** Context.checkSelfPermission só existe na API 23. */
    private boolean hasPermissionCompat(String permission) {
        if (Build.VERSION.SDK_INT >= 23) {
            return checkSelfPermission(permission) == PackageManager.PERMISSION_GRANTED;
        }
        return getPackageManager().checkPermission(permission, getPackageName())
                == PackageManager.PERMISSION_GRANTED;
    }'''


def patch_service():
    path = os.path.join(JAVA_DIR, "MediaPlaybackService.java")
    if not require(path):
        return
    old = read(path)
    src = old

    has_compat_imports = re.search(r"^import (?:androidx|android\.support)\.", src, re.M)
    if "private void startForegroundCompat()" in src and not has_compat_imports:
        skipped.append("%s (service: já estava ok)" % rel(path))
        return

    # --- imports -------------------------------------------------------
    src = re.sub(r"^import (?:androidx|android\.support)\.[\w.$]+;[ \t]*\n", "",
                 src, flags=re.M)
    missing = [i for i in NEW_IMPORTS if i not in src]
    if missing:
        anchor = "import android.media.AudioManager;"
        if anchor in src:
            src = src.replace(anchor, anchor + "\n" + "\n".join(missing), 1)
        else:
            problems.append("MediaPlaybackService: não achei a âncora de imports")

    # --- campos / criação ---------------------------------------------
    src = src.replace("private MediaSessionCompat mSession;",
                      "private MediaSession mSession; // API 21+ (null em versões antigas)")
    src = src.replace("private NotificationManagerCompat mNotificationManagerCompat;",
                      "private NotificationManager mNotificationManager;")
    src = src.replace("NotificationManagerCompat.from(this)",
                      "(NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE)")
    src = src.replace("mNotificationManagerCompat", "mNotificationManager")

    # --- chamadas soltas (ANTES de inserir os helpers novos) -----------
    src = re.sub(r"stopForeground\(\s*Service\.STOP_FOREGROUND_REMOVE\s*\)",
                 "stopForegroundCompat(true)", src)
    src = re.sub(r"stopForeground\(\s*Service\.STOP_FOREGROUND_DETACH\s*\)",
                 "stopForegroundCompat(false)", src)
    src = re.sub(r"startForeground\(\s*PLAYBACKSERVICE_STATUS\s*,\s*buildNotification\(\)\s*\)",
                 "startForegroundCompat()", src)
    src = re.sub(r"mNotificationManager\.notify\(\s*PLAYBACKSERVICE_STATUS\s*,"
                 r"\s*buildNotification\(\)\s*\)", "notifyCompat()", src)
    src = re.sub(r"checkSelfPermission\(([^()]*)\)\s*==\s*PackageManager\.PERMISSION_GRANTED",
                 r"hasPermissionCompat(\1)", src)

    # --- métodos inteiros ----------------------------------------------
    for name, text in (("createNotificationChannel", M_CREATE_CHANNEL),
                       ("setUpMediaSession", M_SETUP_SESSION),
                       ("updateMediaSession", M_UPDATE_SESSION),
                       ("buildNotification", M_BUILD_NOTIFICATION)):
        src, ok = replace_method(src, name, text)
        if not ok:
            problems.append("MediaPlaybackService: método %s não encontrado" % name)

    # --- helpers novos, logo depois de buildNotification ---------------
    if "private void startForegroundCompat()" not in src:
        m = re.search(r"private Notification buildNotification\(\)\s*\{", src)
        if m:
            end = match_brace(src, m.end() - 1)
            src = src[:end + 1] + HELPERS + src[end + 1:]
        else:
            problems.append("MediaPlaybackService: não consegui inserir os helpers")

    finish(path, old, src, "androidx -> framework")


# ----------------------------------------------------------------------------
# 5. MusicBrowserActivity.java
# ----------------------------------------------------------------------------
def patch_browser_activity():
    path = os.path.join(JAVA_DIR, "MusicBrowserActivity.java")
    if not require(path):
        return
    old = read(path)
    new = re.sub(r"^import androidx\.[\w.$]+;[ \t]*\n(?:[ \t]*\n)?", "", old, flags=re.M)
    new = re.sub(r"ActivityCompat\.checkSelfPermission\(\s*this\s*,\s*", "checkSelfPermission(", new)
    new = re.sub(r"ActivityCompat\.requestPermissions\(\s*this\s*,\s*", "requestPermissions(", new)
    finish(path, old, new, "ActivityCompat -> Activity")


# ----------------------------------------------------------------------------
# 6. MediaButtonIntentReceiver.java
# ----------------------------------------------------------------------------
RECEIVER_HELPER = r'''    /** Inicia o service em foreground no Android 8+ (API 26); antes, startService normal. */
    private static void startServiceCompat(Context context, Intent intent) {
        if (Build.VERSION.SDK_INT >= 26) {
            context.startForegroundService(intent);
        } else {
            context.startService(intent);
        }
    }

'''


def patch_button_receiver():
    path = os.path.join(JAVA_DIR, "MediaButtonIntentReceiver.java")
    if not require(path):
        return
    old = read(path)
    if "private static void startServiceCompat(" in old and "import androidx." not in old:
        skipped.append("%s (receiver: já estava ok)" % rel(path))
        return
    new = re.sub(r"^import androidx\.[\w.$]+;[ \t]*\n(?:[ \t]*\n)?", "", old, flags=re.M)
    new = new.replace("ContextCompat.startForegroundService(", "startServiceCompat(")
    if "import android.os.Build;" not in new:
        new = new.replace("import android.os.Handler;",
                          "import android.os.Build;\nimport android.os.Handler;", 1)
    if "startServiceCompat(Context" not in new:
        m = re.search(r"^[ \t]*@Override\s*\n[ \t]*public void onReceive", new, re.M)
        if m:
            new = new[:m.start()] + RECEIVER_HELPER + new[m.start():]
        else:
            problems.append("MediaButtonIntentReceiver: não achei onReceive")
    finish(path, old, new, "ContextCompat -> helper local")


# ----------------------------------------------------------------------------
# 7. strings.xml (avisos de formato não posicional)
# ----------------------------------------------------------------------------
def patch_strings():
    if not os.path.isdir(RES_DIR):
        problems.append("pasta de resources não encontrada: %s" % rel(RES_DIR))
        return
    pat = re.compile(r'<string name="rename_playlist_diff_prompt"(?![^>]*\bformatted=)')
    n_files = 0
    for d in sorted(os.listdir(RES_DIR)):
        if not d.startswith("values"):
            continue
        folder = os.path.join(RES_DIR, d)
        for f in sorted(os.listdir(folder)):
            if not f.endswith(".xml"):
                continue
            p = os.path.join(folder, f)
            old = read(p)
            new = pat.sub('<string name="rename_playlist_diff_prompt" formatted="false"', old)
            if new != old:
                write(p, new)
                n_files += 1
    if n_files:
        changed.append("res/values*/strings.xml (formatted=\"false\" em %d arquivos)" % n_files)
    else:
        skipped.append("res/values*/strings.xml (já estava ok)")


# ----------------------------------------------------------------------------
# verificação final
# ----------------------------------------------------------------------------
LEFTOVER = re.compile(r"androidx|android\.support|ContextCompat|ActivityCompat|"
                      r"NotificationCompat|MediaSessionCompat|PlaybackStateCompat|"
                      r"MediaMetadataCompat|NotificationManagerCompat|"
                      r"NotificationChannelCompat|MediaButtonReceiver")


def verify():
    left = []
    targets = [os.path.join(ROOT, "build.gradle"), os.path.join(ROOT, "settings.gradle"),
               os.path.join(ROOT, "gradle.properties"),
               os.path.join(ROOT, "app", "build.gradle"),
               os.path.join(ROOT, "app", "proguard-rules.pro"),
               os.path.join(ROOT, "app", "src", "main", "AndroidManifest.xml")]
    for base, _, files in os.walk(os.path.join(ROOT, "app", "src")):
        for f in files:
            if f.endswith((".java", ".xml", ".aidl")):
                targets.append(os.path.join(base, f))
    for p in targets:
        if not os.path.isfile(p):
            continue
        for ln, line in enumerate(read(p).split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith(("//", "/*", "*", "#", "<!--")):
                continue  # comentários não contam
            if LEFTOVER.search(line):
                left.append("%s:%d: %s" % (rel(p), ln, line.strip()))
    return left


def main():
    if not os.path.isfile(os.path.join(ROOT, "settings.gradle")) or \
            not os.path.isdir(os.path.join(ROOT, "app")):
        print("ERRO: rode na raiz do repo (onde ficam settings.gradle e a pasta app/).")
        return 2

    print("== fix_remove_androidx %s==" % ("(dry-run) " if DRY else ""))
    patch_app_gradle()
    patch_gradle_properties()
    patch_proguard()
    patch_service()
    patch_browser_activity()
    patch_button_receiver()
    patch_strings()

    print("\nAlterados:")
    for c in changed:
        print("  + " + c)
    if not changed:
        print("  (nada)")
    print("\nJá ok / ignorados:")
    for s in skipped:
        print("  = " + s)

    left = [] if DRY else verify()
    if left:
        problems.append("ainda restam referências a androidx/compat:")
        problems.extend("    " + l for l in left)

    if problems:
        print("\nPROBLEMAS:")
        for p in problems:
            print("  ! " + p)
        return 1

    print("\nOK. Agora rode:  gradle clean assembleDebug")
    return 0


if __name__ == "__main__":
    sys.exit(main())
