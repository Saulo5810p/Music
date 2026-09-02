#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_search_feature.py

Aplica a feature de "busca inline por nome" nas 4 abas do app Music
(Tracks, Albums, Artists, Playlists), reaproveitando o filtro de
ListView/ExpandableListView (setTextFilterEnabled + setFilterText)
que ja existe no projeto, em vez de abrir a busca global do sistema
Android (QueryBrowserActivity / SearchManager).

O QUE MUDA:
  - app/src/main/res/layout/media_picker_activity.xml
  - app/src/main/res/layout/media_picker_activity_expanding.xml
  - app/src/main/java/com/android/music/TrackBrowserActivity.java
  - app/src/main/java/com/android/music/AlbumBrowserActivity.java
  - app/src/main/java/com/android/music/ArtistAlbumBrowserActivity.java
  - app/src/main/java/com/android/music/PlaylistBrowserActivity.java

COMO USAR (Termux):
  1. cd para a raiz do repo clonado (onde tem a pasta "app/" e "settings.gradle")
  2. python3 apply_search_feature.py
  3. Revise o diff impresso, depois: ./gradlew assembleDebug

O script:
  - Confere que voce esta na raiz certa do repo (existe app/src/main/java/com/android/music)
  - Se o diretorio for um repo git, tenta "git apply" (mais seguro, com --check antes)
  - Se nao for git (ou git apply falhar), aplica um patch manual arquivo por arquivo,
    fazendo backup .bak de cada arquivo tocado antes de escrever
  - E idempotente: se detectar que a mudanca ja foi aplicada num arquivo, pula esse arquivo
"""

import os
import sys
import subprocess
import shutil

PATCH_TEXT = r'''diff --git a/app/src/main/java/com/android/music/AlbumBrowserActivity.java b/app/src/main/java/com/android/music/AlbumBrowserActivity.java
index 1b7edac..a7c8329 100644
--- a/app/src/main/java/com/android/music/AlbumBrowserActivity.java
+++ b/app/src/main/java/com/android/music/AlbumBrowserActivity.java
@@ -54,7 +54,10 @@ import android.widget.ListView;
 import android.widget.SectionIndexer;
 import android.widget.SimpleCursorAdapter;
 import android.widget.TextView;
+import android.widget.EditText;
 import android.widget.AdapterView.AdapterContextMenuInfo;
+import android.text.Editable;
+import android.text.TextWatcher;
 
 import java.text.Collator;
 import android.os.Build;
@@ -67,7 +70,9 @@ public class AlbumBrowserActivity extends ListActivity
     private String mCurrentArtistNameForAlbum;
     private AlbumListAdapter mAdapter;
     private boolean mAdapterSent;
+    private EditText mSearchBox;
     private final static int SEARCH = CHILD_MENU_BASE;
+    private final static int SEARCH_INLINE = CHILD_MENU_BASE + 20;
 
     public AlbumBrowserActivity()
     {
@@ -104,6 +109,7 @@ public class AlbumBrowserActivity extends ListActivity
         lv.setFastScrollEnabled(true);
         lv.setOnCreateContextMenuListener(this);
         lv.setTextFilterEnabled(true);
+        setupSearchBox();
 
         mAdapter = (AlbumListAdapter) getLastNonConfigurationInstance();
         if (mAdapter == null) {
@@ -331,6 +337,45 @@ public class AlbumBrowserActivity extends ListActivity
         startActivity(Intent.createChooser(i, title));
     }
 
+    /**
+     * Wires up the inline search box (shared media_picker_activity layout)
+     * to the list's own text filter, so typing an album name filters this
+     * tab's list in place, reusing the existing filter/LIKE-query machinery.
+     */
+    private void setupSearchBox() {
+        mSearchBox = (EditText) findViewById(R.id.search_box);
+        if (mSearchBox == null) {
+            return;
+        }
+        mSearchBox.addTextChangedListener(new TextWatcher() {
+            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
+            public void onTextChanged(CharSequence s, int start, int before, int count) {
+                ListView lv = getListView();
+                if (lv != null) {
+                    if (s.length() == 0) {
+                        lv.clearTextFilter();
+                    } else {
+                        lv.setFilterText(s.toString());
+                    }
+                }
+            }
+            public void afterTextChanged(Editable s) {}
+        });
+    }
+
+    private void toggleSearchBox() {
+        if (mSearchBox == null) {
+            return;
+        }
+        if (mSearchBox.getVisibility() == View.VISIBLE) {
+            mSearchBox.setText("");
+            mSearchBox.setVisibility(View.GONE);
+        } else {
+            mSearchBox.setVisibility(View.VISIBLE);
+            mSearchBox.requestFocus();
+        }
+    }
+
     @Override
     protected void onActivityResult(int requestCode, int resultCode, Intent intent) {
         switch (requestCode) {
@@ -370,6 +415,7 @@ public class AlbumBrowserActivity extends ListActivity
         menu.add(0, GOTO_START, 0, R.string.goto_start).setIcon(R.drawable.ic_menu_music_library);
         menu.add(0, GOTO_PLAYBACK, 0, R.string.goto_playback).setIcon(R.drawable.ic_menu_playback);
         menu.add(0, SHUFFLE_ALL, 0, R.string.shuffle_all).setIcon(R.drawable.ic_menu_shuffle);
+        menu.add(0, SEARCH_INLINE, 0, R.string.search_title).setIcon(android.R.drawable.ic_menu_search);
         return true;
     }
 
@@ -406,6 +452,10 @@ public class AlbumBrowserActivity extends ListActivity
                     cursor.close();
                 }
                 return true;
+
+            case SEARCH_INLINE:
+                toggleSearchBox();
+                return true;
         }
         return super.onOptionsItemSelected(item);
     }
diff --git a/app/src/main/java/com/android/music/ArtistAlbumBrowserActivity.java b/app/src/main/java/com/android/music/ArtistAlbumBrowserActivity.java
index aab6ae6..bdc7754 100644
--- a/app/src/main/java/com/android/music/ArtistAlbumBrowserActivity.java
+++ b/app/src/main/java/com/android/music/ArtistAlbumBrowserActivity.java
@@ -55,7 +55,10 @@ import android.widget.ImageView;
 import android.widget.SectionIndexer;
 import android.widget.SimpleCursorTreeAdapter;
 import android.widget.TextView;
+import android.widget.EditText;
 import android.widget.ExpandableListView.ExpandableListContextMenuInfo;
+import android.text.Editable;
+import android.text.TextWatcher;
 
 import java.text.Collator;
 import android.os.Build;
@@ -71,7 +74,9 @@ public class ArtistAlbumBrowserActivity extends ExpandableListActivity
     private String mCurrentArtistNameForAlbum;
     private ArtistAlbumListAdapter mAdapter;
     private boolean mAdapterSent;
+    private EditText mSearchBox;
     private final static int SEARCH = CHILD_MENU_BASE;
+    private final static int SEARCH_INLINE = CHILD_MENU_BASE + 20;
 
     public ArtistAlbumBrowserActivity()
     {
@@ -107,6 +112,7 @@ public class ArtistAlbumBrowserActivity extends ExpandableListActivity
         lv.setFastScrollEnabled(true);
         lv.setOnCreateContextMenuListener(this);
         lv.setTextFilterEnabled(true);
+        setupSearchBox();
 
         mAdapter = (ArtistAlbumListAdapter) getLastNonConfigurationInstance();
         if (mAdapter == null) {
@@ -264,6 +270,7 @@ public class ArtistAlbumBrowserActivity extends ExpandableListActivity
         menu.add(0, GOTO_START, 0, R.string.goto_start).setIcon(R.drawable.ic_menu_music_library);
         menu.add(0, GOTO_PLAYBACK, 0, R.string.goto_playback).setIcon(R.drawable.ic_menu_playback);
         menu.add(0, SHUFFLE_ALL, 0, R.string.shuffle_all).setIcon(R.drawable.ic_menu_shuffle);
+        menu.add(0, SEARCH_INLINE, 0, R.string.search_title).setIcon(android.R.drawable.ic_menu_search);
         return true;
     }
     
@@ -300,10 +307,54 @@ public class ArtistAlbumBrowserActivity extends ExpandableListActivity
                     cursor.close();
                 }
                 return true;
+
+            case SEARCH_INLINE:
+                toggleSearchBox();
+                return true;
         }
         return super.onOptionsItemSelected(item);
     }
 
+    /**
+     * Wires up the inline search box (shared media_picker_activity_expanding
+     * layout) to the expandable list's own text filter, so typing an artist
+     * or album name filters this tab's list in place, reusing the existing
+     * filter/LIKE-query machinery.
+     */
+    private void setupSearchBox() {
+        mSearchBox = (EditText) findViewById(R.id.search_box);
+        if (mSearchBox == null) {
+            return;
+        }
+        mSearchBox.addTextChangedListener(new TextWatcher() {
+            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
+            public void onTextChanged(CharSequence s, int start, int before, int count) {
+                ExpandableListView lv = getExpandableListView();
+                if (lv != null) {
+                    if (s.length() == 0) {
+                        lv.clearTextFilter();
+                    } else {
+                        lv.setFilterText(s.toString());
+                    }
+                }
+            }
+            public void afterTextChanged(Editable s) {}
+        });
+    }
+
+    private void toggleSearchBox() {
+        if (mSearchBox == null) {
+            return;
+        }
+        if (mSearchBox.getVisibility() == View.VISIBLE) {
+            mSearchBox.setText("");
+            mSearchBox.setVisibility(View.GONE);
+        } else {
+            mSearchBox.setVisibility(View.VISIBLE);
+            mSearchBox.requestFocus();
+        }
+    }
+
     @Override
     public void onCreateContextMenu(ContextMenu menu, View view, ContextMenuInfo menuInfoIn) {
         menu.add(0, PLAY_SELECTION, 0, R.string.play_selection);
diff --git a/app/src/main/java/com/android/music/PlaylistBrowserActivity.java b/app/src/main/java/com/android/music/PlaylistBrowserActivity.java
index 196248a..0984ac5 100644
--- a/app/src/main/java/com/android/music/PlaylistBrowserActivity.java
+++ b/app/src/main/java/com/android/music/PlaylistBrowserActivity.java
@@ -54,7 +54,10 @@ import android.widget.ListView;
 import android.widget.SimpleCursorAdapter;
 import android.widget.TextView;
 import android.widget.Toast;
+import android.widget.EditText;
 import android.widget.AdapterView.AdapterContextMenuInfo;
+import android.text.Editable;
+import android.text.TextWatcher;
 import android.os.Build;
 
 public class PlaylistBrowserActivity extends ListActivity
@@ -65,11 +68,13 @@ public class PlaylistBrowserActivity extends ListActivity
     private static final int EDIT_PLAYLIST = CHILD_MENU_BASE + 2;
     private static final int RENAME_PLAYLIST = CHILD_MENU_BASE + 3;
     private static final int CHANGE_WEEKS = CHILD_MENU_BASE + 4;
+    private static final int SEARCH_INLINE = CHILD_MENU_BASE + 5;
     private static final long RECENTLY_ADDED_PLAYLIST = -1;
     private static final long ALL_SONGS_PLAYLIST = -2;
     private static final long PODCASTS_PLAYLIST = -3;
     private PlaylistListAdapter mAdapter;
     boolean mAdapterSent;
+    private EditText mSearchBox;
 
     private boolean mCreateShortcut;
 
@@ -130,6 +135,9 @@ public class PlaylistBrowserActivity extends ListActivity
         ListView lv = getListView();
         lv.setOnCreateContextMenuListener(this);
         lv.setTextFilterEnabled(true);
+        if (!mCreateShortcut) {
+            setupSearchBox();
+        }
 
         mAdapter = (PlaylistListAdapter) getLastNonConfigurationInstance();
         if (mAdapter == null) {
@@ -238,6 +246,8 @@ public class PlaylistBrowserActivity extends ListActivity
                     R.drawable.ic_menu_music_library);
             menu.add(0, GOTO_PLAYBACK, 0, R.string.goto_playback).setIcon(
                     R.drawable.ic_menu_playback).setVisible(MusicUtils.isMusicLoaded());
+            menu.add(0, SEARCH_INLINE, 0, R.string.search_title).setIcon(
+                    android.R.drawable.ic_menu_search);
         }
         return super.onCreateOptionsMenu(menu);
     }
@@ -257,9 +267,52 @@ public class PlaylistBrowserActivity extends ListActivity
                 intent = new Intent("com.android.music.PLAYBACK_VIEWER");
                 startActivity(intent);
                 return true;
+
+            case SEARCH_INLINE:
+                toggleSearchBox();
+                return true;
         }
         return super.onOptionsItemSelected(item);
     }
+
+    /**
+     * Wires up the inline search box (shared media_picker_activity layout)
+     * to the list's own text filter, so typing a playlist name filters this
+     * tab's list in place, reusing the existing filter/LIKE-query machinery.
+     */
+    private void setupSearchBox() {
+        mSearchBox = (EditText) findViewById(R.id.search_box);
+        if (mSearchBox == null) {
+            return;
+        }
+        mSearchBox.addTextChangedListener(new TextWatcher() {
+            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
+            public void onTextChanged(CharSequence s, int start, int before, int count) {
+                ListView lv = getListView();
+                if (lv != null) {
+                    if (s.length() == 0) {
+                        lv.clearTextFilter();
+                    } else {
+                        lv.setFilterText(s.toString());
+                    }
+                }
+            }
+            public void afterTextChanged(Editable s) {}
+        });
+    }
+
+    private void toggleSearchBox() {
+        if (mSearchBox == null) {
+            return;
+        }
+        if (mSearchBox.getVisibility() == View.VISIBLE) {
+            mSearchBox.setText("");
+            mSearchBox.setVisibility(View.GONE);
+        } else {
+            mSearchBox.setVisibility(View.VISIBLE);
+            mSearchBox.requestFocus();
+        }
+    }
     
     public void onCreateContextMenu(ContextMenu menu, View view, ContextMenuInfo menuInfoIn) {
         if (mCreateShortcut) {
diff --git a/app/src/main/java/com/android/music/TrackBrowserActivity.java b/app/src/main/java/com/android/music/TrackBrowserActivity.java
index 718696f..84502f2 100644
--- a/app/src/main/java/com/android/music/TrackBrowserActivity.java
+++ b/app/src/main/java/com/android/music/TrackBrowserActivity.java
@@ -57,7 +57,10 @@ import android.widget.ListView;
 import android.widget.SectionIndexer;
 import android.widget.SimpleCursorAdapter;
 import android.widget.TextView;
+import android.widget.EditText;
 import android.widget.AdapterView.AdapterContextMenuInfo;
+import android.text.Editable;
+import android.text.TextWatcher;
 
 import java.text.Collator;
 import java.util.Arrays;
@@ -73,6 +76,7 @@ public class TrackBrowserActivity extends ListActivity
     private static final int CLEAR_PLAYLIST = CHILD_MENU_BASE + 4;
     private static final int REMOVE = CHILD_MENU_BASE + 5;
     private static final int SEARCH = CHILD_MENU_BASE + 6;
+    private static final int SEARCH_INLINE = CHILD_MENU_BASE + 7;
 
 
     private static final String LOGTAG = "TrackBrowser";
@@ -85,6 +89,7 @@ public class TrackBrowserActivity extends ListActivity
     private String mCurrentAlbumName;
     private String mCurrentArtistNameForAlbum;
     private ListView mTrackList;
+    private EditText mSearchBox;
     private Cursor mTrackCursor;
     private TrackListAdapter mAdapter;
     private boolean mAdapterSent = false;
@@ -157,6 +162,7 @@ public class TrackBrowserActivity extends ListActivity
             mTrackList.setCacheColorHint(0);
         } else {
             mTrackList.setTextFilterEnabled(true);
+            setupSearchBox();
         }
         mAdapter = (TrackListAdapter) getLastNonConfigurationInstance();
         
@@ -686,6 +692,44 @@ public class TrackBrowserActivity extends ListActivity
         startActivity(Intent.createChooser(i, title));
     }
 
+    /**
+     * Wires up the inline search box (shared media_picker_activity layout)
+     * to the list's own text filter, so typing a song title filters this
+     * tab's list in place, reusing the existing filter/LIKE-query machinery.
+     */
+    private void setupSearchBox() {
+        mSearchBox = (EditText) findViewById(R.id.search_box);
+        if (mSearchBox == null) {
+            return;
+        }
+        mSearchBox.addTextChangedListener(new TextWatcher() {
+            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
+            public void onTextChanged(CharSequence s, int start, int before, int count) {
+                if (mTrackList != null) {
+                    if (s.length() == 0) {
+                        mTrackList.clearTextFilter();
+                    } else {
+                        mTrackList.setFilterText(s.toString());
+                    }
+                }
+            }
+            public void afterTextChanged(Editable s) {}
+        });
+    }
+
+    private void toggleSearchBox() {
+        if (mSearchBox == null) {
+            return;
+        }
+        if (mSearchBox.getVisibility() == View.VISIBLE) {
+            mSearchBox.setText("");
+            mSearchBox.setVisibility(View.GONE);
+        } else {
+            mSearchBox.setVisibility(View.VISIBLE);
+            mSearchBox.requestFocus();
+        }
+    }
+
     // In order to use alt-up/down as a shortcut for moving the selected item
     // in the list, we need to override dispatchKeyEvent, not onKeyDown.
     // (onKeyDown never sees these events, since they are handled by the list)
@@ -828,6 +872,10 @@ public class TrackBrowserActivity extends ListActivity
                 menu.add(0, CLEAR_PLAYLIST, 0, R.string.clear_playlist).setIcon(android.R.drawable.ic_menu_close_clear_cancel);
             }
         }
+        if (!mEditMode) {
+            menu.add(0, SEARCH_INLINE, 0, R.string.search_title)
+                    .setIcon(android.R.drawable.ic_menu_search);
+        }
         return true;
     }
 
@@ -841,6 +889,10 @@ public class TrackBrowserActivity extends ListActivity
                 return true;
             }
 
+            case SEARCH_INLINE:
+                toggleSearchBox();
+                return true;
+
             case GOTO_START:
                 intent = new Intent();
                 intent.setClass(this, MusicBrowserActivity.class);
diff --git a/app/src/main/res/layout/media_picker_activity.xml b/app/src/main/res/layout/media_picker_activity.xml
index 79f080e..8ca0420 100644
--- a/app/src/main/res/layout/media_picker_activity.xml
+++ b/app/src/main/res/layout/media_picker_activity.xml
@@ -22,6 +22,17 @@
 
     <include layout="@layout/sd_error" />
 
+    <EditText
+        android:id="@+id/search_box"
+        android:layout_width="fill_parent"
+        android:layout_height="wrap_content"
+        android:layout_margin="8dip"
+        android:hint="@string/search_title"
+        android:singleLine="true"
+        android:imeOptions="actionDone"
+        android:inputType="text"
+        android:visibility="gone" />
+
     <com.android.music.TouchInterceptor
         android:id="@android:id/list"
         android:layout_width="fill_parent"
diff --git a/app/src/main/res/layout/media_picker_activity_expanding.xml b/app/src/main/res/layout/media_picker_activity_expanding.xml
index 3361431..7dc45ab 100644
--- a/app/src/main/res/layout/media_picker_activity_expanding.xml
+++ b/app/src/main/res/layout/media_picker_activity_expanding.xml
@@ -22,6 +22,17 @@
 
     <include layout="@layout/sd_error" />
 
+    <EditText
+        android:id="@+id/search_box"
+        android:layout_width="fill_parent"
+        android:layout_height="wrap_content"
+        android:layout_margin="8dip"
+        android:hint="@string/search_title"
+        android:singleLine="true"
+        android:imeOptions="actionDone"
+        android:inputType="text"
+        android:visibility="gone" />
+
     <ExpandableListView
         android:id="@android:id/list"
         android:layout_width="fill_parent"
'''

MARKER = "setupSearchBox"  # presenca disso no arquivo = ja aplicado

REQUIRED_FILES = [
    "app/src/main/java/com/android/music/TrackBrowserActivity.java",
    "app/src/main/java/com/android/music/AlbumBrowserActivity.java",
    "app/src/main/java/com/android/music/ArtistAlbumBrowserActivity.java",
    "app/src/main/java/com/android/music/PlaylistBrowserActivity.java",
    "app/src/main/res/layout/media_picker_activity.xml",
    "app/src/main/res/layout/media_picker_activity_expanding.xml",
]


def die(msg):
    print("ERRO: " + msg)
    sys.exit(1)


def check_repo_root():
    missing = [f for f in REQUIRED_FILES if not os.path.isfile(f)]
    if missing:
        print("Nao encontrei os seguintes arquivos a partir do diretorio atual:")
        for m in missing:
            print("  - " + m)
        die("Rode este script a partir da RAIZ do repo Music (onde fica a pasta 'app/').")


def already_applied():
    target = "app/src/main/java/com/android/music/TrackBrowserActivity.java"
    with open(target, "r", encoding="utf-8", errors="ignore") as f:
        return MARKER in f.read()


def is_git_repo():
    return os.path.isdir(".git")


def try_git_apply():
    patch_path = "_search_feature.patch"
    with open(patch_path, "w", encoding="utf-8") as f:
        f.write(PATCH_TEXT)
    try:
        check = subprocess.run(
            ["git", "apply", "--check", patch_path],
            capture_output=True, text=True
        )
        if check.returncode != 0:
            print("git apply --check falhou, vou tentar o modo manual.")
            print(check.stderr)
            return False
        apply = subprocess.run(
            ["git", "apply", patch_path],
            capture_output=True, text=True
        )
        if apply.returncode != 0:
            print("git apply falhou na aplicacao real:")
            print(apply.stderr)
            return False
        print("Patch aplicado via git apply com sucesso.")
        return True
    finally:
        if os.path.exists(patch_path):
            os.remove(patch_path)


# --- Modo manual: parse simples de unified diff (+ context, - removido, + adicionado) ---
def parse_unified_diff(patch_text):
    """Retorna lista de (caminho_arquivo, lista_de_hunks).
    Cada hunk = lista de linhas com prefixo (' ', '+', '-')."""
    files = []
    current_file = None
    current_hunks = None
    current_hunk = None
    lines = patch_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("diff --git"):
            if current_file and current_hunks is not None:
                if current_hunk is not None:
                    current_hunks.append(current_hunk)
                files.append((current_file, current_hunks))
            current_file = None
            current_hunks = []
            current_hunk = None
        elif line.startswith("+++ b/"):
            current_file = line[len("+++ b/"):]
        elif line.startswith("@@"):
            if current_hunk is not None:
                current_hunks.append(current_hunk)
            current_hunk = []
        elif current_hunk is not None and (line.startswith(" ") or line.startswith("+") or line.startswith("-")):
            current_hunk.append(line)
        elif line.startswith("\\ No newline"):
            pass
        i += 1
    if current_file and current_hunks is not None:
        if current_hunk is not None:
            current_hunks.append(current_hunk)
        files.append((current_file, current_hunks))
    return files


def apply_hunk_to_lines(file_lines, hunk):
    """Aplica um hunk (lista de linhas com prefixo) a file_lines (lista de str sem \n).
    Localiza o bloco de contexto+remocao no arquivo e substitui pelo bloco de contexto+adicao."""
    old_block = []
    new_block = []
    for hl in hunk:
        tag, content = hl[0], hl[1:]
        if tag == " ":
            old_block.append(content)
            new_block.append(content)
        elif tag == "-":
            old_block.append(content)
        elif tag == "+":
            new_block.append(content)

    n = len(old_block)
    if n == 0:
        return file_lines, False

    for start in range(0, len(file_lines) - n + 1):
        if file_lines[start:start + n] == old_block:
            return file_lines[:start] + new_block + file_lines[start + n:], True
    return file_lines, False


def manual_apply():
    parsed = parse_unified_diff(PATCH_TEXT)
    ok_all = True
    for relpath, hunks in parsed:
        if not os.path.isfile(relpath):
            print("Pulei (nao encontrado): " + relpath)
            ok_all = False
            continue

        with open(relpath, "r", encoding="utf-8") as f:
            original_text = f.read()
        file_lines = original_text.split("\n")

        applied_any = False
        for hunk in hunks:
            file_lines, ok = apply_hunk_to_lines(file_lines, hunk)
            if ok:
                applied_any = True
            else:
                print("AVISO: um trecho de " + relpath + " nao bateu (talvez ja aplicado ou arquivo mudou). Pulando esse trecho.")

        if applied_any:
            backup_path = relpath + ".bak"
            shutil.copyfile(relpath, backup_path)
            new_text = "\n".join(file_lines)
            with open(relpath, "w", encoding="utf-8") as f:
                f.write(new_text)
            print("Atualizado: " + relpath + "  (backup em " + backup_path + ")")
        else:
            print("Nada aplicado em: " + relpath)
            ok_all = False

    return ok_all


def main():
    check_repo_root()

    if already_applied():
        print("A feature de busca inline ja parece estar aplicada (encontrei 'setupSearchBox' em TrackBrowserActivity.java).")
        print("Nada a fazer. Se quiser reaplicar do zero, restaure os arquivos originais primeiro.")
        return

    print("Aplicando patch: busca inline por nome nas abas Tracks/Albums/Artists/Playlists...")

    success = False
    if is_git_repo():
        print("Repo git detectado, tentando 'git apply'...")
        success = try_git_apply()

    if not success:
        print("Aplicando patch manualmente (arquivo por arquivo)...")
        success = manual_apply()

    if success:
        print()
        print("Concluido. Arquivos alterados:")
        for f in REQUIRED_FILES:
            print("  - " + f)
        print()
        print("Proximo passo: ./gradlew assembleDebug")
    else:
        print()
        print("Nao foi possivel aplicar tudo automaticamente.")
        print("Verifique se o repo esta com o codigo original (sem alteracoes previas nesses arquivos)")
        print("e rode novamente. Backups .bak (se algo foi escrito) ficam ao lado dos arquivos originais.")
        sys.exit(1)


if __name__ == "__main__":
    main()
