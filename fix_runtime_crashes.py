#!/usr/bin/env python3
"""
fix_runtime_crashes.py

Corrige os 6 crashes de runtime reportados após o build compilar
com sucesso:

  1. MediaPlaybackService.onCreate: SecurityException: listen
     -> tmgr.listen(mPhoneStateListener, ...) roda sem checar se
        READ_PHONE_STATE já foi CONCEDIDA. O runtime request feito
        em MusicBrowserActivity só pede a permissão; não garante
        que ela já está concedida no momento em que o serviço é
        criado (pode ser criado antes do usuário responder ao
        diálogo, ou em restart automático do sistema).
        Correção: checar checkSelfPermission antes de chamar listen()
        tanto no onCreate (registro) quanto no onDestroy
        (desregistro).

  2. IllegalArgumentException: Invalid column audio._id as _id
     -> "audio._id AS _id" é sintaxe do ContentProvider antigo
        (Android 1.6/2.x), que expunha a tabela SQL diretamente.
        O MediaStore moderno (escoped storage) não aceita mais
        aliases de tabela qualificados na projeção.
        Correção: trocar por MediaStore.Audio.Media._ID puro.

  3. NullPointerException em MediaPlaybackService.onStart:
     intent.getAction() em intent nulo
     -> onStart() é o método legado; o sistema pode chamar com
        intent == null em restarts automáticos do serviço.
        Correção: retornar cedo se intent == null.

  4. IllegalArgumentException: Invalid column count(*)
     -> "count(*)" como projeção crua não é mais aceito pelo
        MediaStore moderno.
        Correção: buscar _ID e usar cursor.getCount() (API pública
        correta para contar linhas), em MusicUtils.addToPlaylist e
        PlaylistBrowserActivity.mergedCursor.

  5. SecurityException: MODE_WORLD_READABLE no longer supported
     -> TouchInterceptor usava getSharedPreferences("Music", 3),
        onde 3 = MODE_WORLD_READABLE | MODE_WORLD_WRITEABLE,
        removido desde Android 7 (API 24).
        Correção: trocar por Context.MODE_PRIVATE.

  6. NullPointerException em ArtistAlbumBrowserActivity:
     Cursor.getColumnCount() em cursor nulo
     -> MusicUtils.query() pode legitimamente retornar null, mas
        MyCursorWrapper era construído sem checar isso.
        Correção: retornar null cedo se o cursor da query for null.

Faz backup (.bak7) de cada arquivo antes de editar. Idempotente.

Uso (dentro do Termux, na pasta do projeto Music):
  python fix_runtime_crashes.py
ou apontando o caminho do repo:
  python fix_runtime_crashes.py /caminho/para/Music
"""

import sys
import os
import shutil

PKG_REL = os.path.join("com", "android", "music")


def backup(path):
    bak = path + ".bak7"
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
# 1. MediaPlaybackService: checar permissão antes de tmgr.listen()
# ---------------------------------------------------------------------
MPS_IMPORTS_OLD = "import android.content.ContentResolver;"
MPS_IMPORTS_NEW = (
    "import android.Manifest;\n"
    "import android.content.pm.PackageManager;\n"
    "import android.content.ContentResolver;"
)

MPS_ONCREATE_OLD = '''        TelephonyManager tmgr = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
        tmgr.listen(mPhoneStateListener, PhoneStateListener.LISTEN_CALL_STATE);
        PowerManager pm = (PowerManager)getSystemService(Context.POWER_SERVICE);'''

MPS_ONCREATE_NEW = '''        if (checkSelfPermission(Manifest.permission.READ_PHONE_STATE)
                == PackageManager.PERMISSION_GRANTED) {
            TelephonyManager tmgr = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
            tmgr.listen(mPhoneStateListener, PhoneStateListener.LISTEN_CALL_STATE);
        }
        PowerManager pm = (PowerManager)getSystemService(Context.POWER_SERVICE);'''

MPS_ONDESTROY_OLD = '''        TelephonyManager tmgr = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
        tmgr.listen(mPhoneStateListener, 0);'''

MPS_ONDESTROY_NEW = '''        if (checkSelfPermission(Manifest.permission.READ_PHONE_STATE)
                == PackageManager.PERMISSION_GRANTED) {
            TelephonyManager tmgr = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
            tmgr.listen(mPhoneStateListener, 0);
        }'''

# ---------------------------------------------------------------------
# 2. "audio._id AS _id" -> MediaStore.Audio.Media._ID
# ---------------------------------------------------------------------
MPS_CURSORCOLS_OLD = '"audio._id AS _id",             // index must match IDCOLIDX below'
MPS_CURSORCOLS_NEW = 'MediaStore.Audio.Media._ID,     // index must match IDCOLIDX below'

# ---------------------------------------------------------------------
# 3. onStart: proteger contra intent nulo
# ---------------------------------------------------------------------
MPS_ONSTART_OLD = '''    public void onStart(Intent intent, int startId) {
        mServiceStartId = startId;
        mDelayedStopHandler.removeCallbacksAndMessages(null);
        
        String action = intent.getAction();'''

MPS_ONSTART_NEW = '''    public void onStart(Intent intent, int startId) {
        mServiceStartId = startId;
        mDelayedStopHandler.removeCallbacksAndMessages(null);

        if (intent == null) {
            mDelayedStopHandler.removeCallbacksAndMessages(null);
            Message msg = mDelayedStopHandler.obtainMessage();
            mDelayedStopHandler.sendMessageDelayed(msg, IDLE_DELAY);
            return;
        }

        String action = intent.getAction();'''

# ---------------------------------------------------------------------
# 4a. MusicUtils.addToPlaylist: count(*) -> _ID + getCount()
# ---------------------------------------------------------------------
MU_COUNT_OLD = '''            String[] cols = new String[] {
                    "count(*)"
            };
            Uri uri = MediaStore.Audio.Playlists.Members.getContentUri("external", playlistid);
            Cursor cur = resolver.query(uri, cols, null, null, null);
            cur.moveToFirst();
            int base = cur.getInt(0);
            cur.close();'''

MU_COUNT_NEW = '''            String[] cols = new String[] {
                    MediaStore.Audio.Playlists.Members._ID
            };
            Uri uri = MediaStore.Audio.Playlists.Members.getContentUri("external", playlistid);
            Cursor cur = resolver.query(uri, cols, null, null, null);
            int base = cur != null ? cur.getCount() : 0;
            if (cur != null) {
                cur.close();
            }'''

# ---------------------------------------------------------------------
# 4b. PlaylistBrowserActivity.mergedCursor: count(*) -> _ID + getCount()
# ---------------------------------------------------------------------
PBA_COUNT_OLD = '''        Cursor counter = MusicUtils.query(this, MediaStore.Audio.Media.EXTERNAL_CONTENT_URI,
                new String[] {"count(*)"}, "is_podcast=1", null, null);'''

PBA_COUNT_NEW = '''        Cursor counter = MusicUtils.query(this, MediaStore.Audio.Media.EXTERNAL_CONTENT_URI,
                new String[] {MediaStore.Audio.Media._ID}, "is_podcast=1", null, null);'''

# ---------------------------------------------------------------------
# 5. TouchInterceptor: MODE_WORLD_READABLE -> MODE_PRIVATE
# ---------------------------------------------------------------------
TI_MODE_OLD = 'SharedPreferences pref = context.getSharedPreferences("Music", 3);'
TI_MODE_NEW = 'SharedPreferences pref = context.getSharedPreferences("Music", Context.MODE_PRIVATE);'

# ---------------------------------------------------------------------
# 6. ArtistAlbumBrowserActivity: proteger contra cursor nulo
# ---------------------------------------------------------------------
AABA_NULL_OLD = '''            Cursor c = MusicUtils.query(mActivity,
                    MediaStore.Audio.Artists.Albums.getContentUri("external", id),
                    cols, null, null, MediaStore.Audio.Albums.DEFAULT_SORT_ORDER);
            
            class MyCursorWrapper extends CursorWrapper {'''

AABA_NULL_NEW = '''            Cursor c = MusicUtils.query(mActivity,
                    MediaStore.Audio.Artists.Albums.getContentUri("external", id),
                    cols, null, null, MediaStore.Audio.Albums.DEFAULT_SORT_ORDER);
            if (c == null) {
                return null;
            }

            class MyCursorWrapper extends CursorWrapper {'''


def main():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    base_dir = os.path.abspath(base_dir)
    print(f"[i] Repositório alvo: {base_dir}\n")

    mps_path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "MediaPlaybackService.java")
    mu_path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "MusicUtils.java")
    pba_path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "PlaylistBrowserActivity.java")
    ti_path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "TouchInterceptor.java")
    aaba_path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "ArtistAlbumBrowserActivity.java")

    changed = False

    print("--- 1/6: MediaPlaybackService — checar permissão antes de tmgr.listen() ---")
    changed |= apply_fix(mps_path, MPS_IMPORTS_OLD, MPS_IMPORTS_NEW, "MediaPlaybackService.java (imports)")
    changed |= apply_fix(mps_path, MPS_ONCREATE_OLD, MPS_ONCREATE_NEW, "MediaPlaybackService.java (onCreate)")
    changed |= apply_fix(mps_path, MPS_ONDESTROY_OLD, MPS_ONDESTROY_NEW, "MediaPlaybackService.java (onDestroy)")

    print("\n--- 2/6: MediaPlaybackService — audio._id AS _id ---")
    changed |= apply_fix(mps_path, MPS_CURSORCOLS_OLD, MPS_CURSORCOLS_NEW, "MediaPlaybackService.java (mCursorCols)")

    print("\n--- 3/6: MediaPlaybackService — onStart com intent nulo ---")
    changed |= apply_fix(mps_path, MPS_ONSTART_OLD, MPS_ONSTART_NEW, "MediaPlaybackService.java (onStart)")

    print("\n--- 4/6: count(*) -> _ID + getCount() ---")
    changed |= apply_fix(mu_path, MU_COUNT_OLD, MU_COUNT_NEW, "MusicUtils.java (addToPlaylist)")
    changed |= apply_fix(pba_path, PBA_COUNT_OLD, PBA_COUNT_NEW, "PlaylistBrowserActivity.java (mergedCursor)")

    print("\n--- 5/6: TouchInterceptor — MODE_WORLD_READABLE ---")
    changed |= apply_fix(ti_path, TI_MODE_OLD, TI_MODE_NEW, "TouchInterceptor.java")

    print("\n--- 6/6: ArtistAlbumBrowserActivity — cursor nulo ---")
    changed |= apply_fix(aaba_path, AABA_NULL_OLD, AABA_NULL_NEW, "ArtistAlbumBrowserActivity.java")

    print()
    print("=" * 60)
    if changed:
        print("Correções aplicadas. Agora rode:")
        print()
        print("  ./gradlew clean assembleDebug")
        print()
        print("Reinstale o app e teste: abrir, navegar por artistas/álbuns,")
        print("tocar uma música, abrir playlists, e (se possível) simular")
        print("uma ligação para checar o listener de telefone.")
    else:
        print("Nada para corrigir (já estava tudo aplicado).")
    print("=" * 60)


if __name__ == "__main__":
    main()
