#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_apk_size_reduction.py

Reduz o tamanho do APK final removendo dependencia nao usada e ligando
R8 (minify + shrink) com regras de keep conservadoras para nao quebrar
a notificacao de midia (MediaSessionCompat / NotificationCompat.MediaStyle)
nem o AIDL (IMediaPlaybackService) ja validados funcionando.

O QUE MUDA:
  - app/build.gradle
      * remove a dependencia androidx.appcompat (confirmado: zero uso no
        codigo do app, que usa Activity/ListActivity/ExpandableListActivity
        puros do framework, nao AppCompatActivity)
      * liga minifyEnabled=true em release E debug (R8)
      * liga shrinkResources=true em release
      * aponta para app/proguard-rules.pro
  - app/proguard-rules.pro (arquivo NOVO)
      * regras -keep para: componentes do app (Activity/Service/Receiver/
        AppWidgetProvider), AIDL (IMediaPlaybackService), classes AndroidX
        de midia e notificacao usadas via reflection interna

POR QUE ISSO REDUZ TAMANHO:
  Sem R8 (minifyEnabled false), o DEX final inclui o bytecode INTEIRO de
  toda dependencia declarada, mesmo o que o app nunca chama. Isso explica
  um classes.dex de ~8MB para um app que originalmente (Donut, 2009) tinha
  um dex de ~250KB. appcompat sozinha e uma lib grande (Material Components,
  fragments, temas) e nao tem nenhum import no codigo -- e peso morto puro.
  Ligar o R8 faz ele podar automaticamente o que nao e alcancavel a partir
  do codigo do app + das regras -keep abaixo.

RISCO CONHECIDO E MITIGADO:
  R8 agressivo pode remover por engano classes acessadas via reflection
  (comum nas libs "Compat" do AndroidX) ou via Binder/AIDL, quebrando a
  notificacao de midia ou o IMediaPlaybackService em runtime mesmo com o
  build compilando sem erro. As regras -keep em proguard-rules.pro cobrem
  especificamente essas classes. Ainda assim, TESTE a notificacao de midia
  (play/pause/next/prev, lockscreen) depois de instalar o APK com essas
  mudancas -- e o unico jeito de confirmar 100% num ambiente real.

COMO USAR (Termux):
  1. cd para a raiz do repo clonado (onde tem a pasta "app/")
  2. python3 apply_apk_size_reduction.py
  3. ./gradlew assembleDebug   (ou assembleRelease)
  4. Instale e teste a notificacao de midia antes de confiar no resultado
  5. Compare o tamanho: ls -la app/build/outputs/apk/*/*.apk

O script:
  - Confere que voce esta na raiz certa do repo
  - Se for repo git, tenta "git apply --check" e depois "git apply"
  - Se nao for git (ou falhar), aplica o build.gradle manualmente via
    substituicao de texto, com backup .bak antes de escrever
  - Cria app/proguard-rules.pro (ou avisa e pula se ja existir um)
  - E idempotente: se detectar que ja foi aplicado, nao faz nada
"""

import os
import sys
import subprocess
import shutil

PATCH_TEXT = r'''diff --git a/app/build.gradle b/app/build.gradle
index b33cdd3..9fedd3a 100644
--- a/app/build.gradle
+++ b/app/build.gradle
@@ -25,7 +25,14 @@ android {
 
     buildTypes {
         release {
-            minifyEnabled false
+            minifyEnabled true
+            shrinkResources true
+            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
+        }
+        debug {
+            minifyEnabled true
+            shrinkResources false
+            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
         }
     }
 
@@ -36,7 +43,6 @@ android {
 }
 
 dependencies {
-    implementation 'androidx.appcompat:appcompat:1.7.0'
     implementation 'androidx.media:media:1.7.0'
     implementation 'androidx.core:core:1.13.1'
 }
'''

PROGUARD_RULES = r'''# Regras R8/ProGuard para o port do Music (AOSP Donut -> moderno).
#
# Objetivo: deixar o R8 remover codigo morto das libs AndroidX (appcompat*,
# media, core) sem tocar em nada que o app realmente usa em runtime,
# especialmente coisas acessadas via reflection interna das libs de media
# (MediaSessionCompat / NotificationCompat.MediaStyle / MediaButtonReceiver),
# via AIDL (IMediaPlaybackService), ou via nome de classe no manifest.
#
# *appcompat foi removida do build.gradle por nao ser usada; caso alguem
# volte a adiciona-la no futuro, estas regras nao dependem dela.

# --- Componentes do proprio app declarados no AndroidManifest.xml ---
# O Android Gradle Plugin ja mantem Activities/Services/Receivers/Providers
# citados no manifest automaticamente, mas fixamos explicitamente porque
# varias telas sao abertas por Intent com nome de classe / acao customizada
# (com.android.music.PLAYBACK_VIEWER, MediaAppWidgetProvider, etc.) e
# porque MediaPlaybackService e controlado via AIDL (ver abaixo).
-keep class com.android.music.** extends android.app.Activity { *; }
-keep class com.android.music.** extends android.app.Service { *; }
-keep class com.android.music.** extends android.content.BroadcastReceiver { *; }
-keep class com.android.music.** extends android.appwidget.AppWidgetProvider { *; }

# --- AIDL (IMediaPlaybackService) ---
# Interfaces/Stubs gerados de .aidl sao chamados via Binder por nome de
# metodo/transacao; nao deixar o R8 renomear ou podar nada aqui.
-keep class com.android.music.IMediaPlaybackService { *; }
-keep class com.android.music.IMediaPlaybackService$* { *; }

# --- AndroidX Media (MediaSessionCompat, MediaButtonReceiver, MediaStyle) ---
# Essas classes fazem bastante trabalho via reflection interna para manter
# compatibilidade entre versoes de Android (o motivo de existirem "Compat").
# Sao tambem o coracao da notificacao de midia (foreground service) que ja
# foi validada funcionando — qualquer poda agressiva aqui e o risco real.
-keep class androidx.media.session.MediaButtonReceiver { *; }
-keep class androidx.media.app.NotificationCompat$MediaStyle { *; }
-keep class android.support.v4.media.session.MediaSessionCompat { *; }
-keep class android.support.v4.media.session.MediaSessionCompat$* { *; }
-keep class android.support.v4.media.** { *; }
-dontwarn android.support.v4.media.**

# --- AndroidX Core (NotificationCompat, ContextCompat) ---
-keep class androidx.core.app.NotificationCompat { *; }
-keep class androidx.core.app.NotificationCompat$* { *; }
-keep class androidx.core.app.NotificationChannelCompat { *; }
-keep class androidx.core.app.NotificationChannelCompat$* { *; }
-keep class androidx.core.app.NotificationManagerCompat { *; }
-keep class androidx.core.content.ContextCompat { *; }

# --- Regra generica para *Compat/*Builder usados via reflection em libs AndroidX ---
# Cobre variantes internas que a lib de media cria dinamicamente conforme a
# versao do Android detectada em runtime (padrao comum nessas libs "Compat").
-keep class androidx.media.**Impl* { *; }
-keep class androidx.core.app.**Impl* { *; }

# --- Parcelable / Bundle ---
# Nenhum Parcelable customizado foi encontrado no codigo do app hoje, mas
# a regra padrao e barata e evita quebra silenciosa se um for adicionado.
-keepclassmembers class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}

# --- Enums (padrao seguro, o R8 as vezes poda valueOf/values por engano) ---
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# --- Atributos uteis para stack traces legiveis em logcat ---
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# Nao ofuscar nomes (foco e reduzir tamanho via shrink de codigo morto,
# nao dificultar leitura de logcat/crash — o app nao tem motivo de
# ofuscacao por sigilo, e ofuscacao pura nao ajuda tanto no tamanho
# quanto o shrink em si).
-dontobfuscate
'''

MARKER = "proguardFiles getDefaultProguardFile"  # presenca disso em build.gradle = ja aplicado

REQUIRED_FILES = [
    "app/build.gradle",
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
    with open("app/build.gradle", "r", encoding="utf-8", errors="ignore") as f:
        return MARKER in f.read()


def is_git_repo():
    return os.path.isdir(".git")


def try_git_apply():
    patch_path = "_apk_size_reduction.patch"
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
        print("build.gradle atualizado via git apply com sucesso.")
        return True
    finally:
        if os.path.exists(patch_path):
            os.remove(patch_path)


def manual_apply_build_gradle():
    path = "app/build.gradle"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    old_block = "    buildTypes {\n        release {\n            minifyEnabled false\n        }\n    }"
    new_block = (
        "    buildTypes {\n"
        "        release {\n"
        "            minifyEnabled true\n"
        "            shrinkResources true\n"
        "            proguardFiles getDefaultProguardFile(\'proguard-android-optimize.txt\'), \'proguard-rules.pro\'\n"
        "        }\n"
        "        debug {\n"
        "            minifyEnabled true\n"
        "            shrinkResources false\n"
        "            proguardFiles getDefaultProguardFile(\'proguard-android-optimize.txt\'), \'proguard-rules.pro\'\n"
        "        }\n"
        "    }"
    )

    if old_block not in text:
        print("AVISO: nao encontrei o bloco buildTypes esperado em app/build.gradle.")
        print("Pode ser que o arquivo ja tenha sido customizado. Edite manualmente:")
        print("  - buildTypes.release.minifyEnabled = true")
        print("  - adicione buildTypes.debug com minifyEnabled = true")
        print("  - aponte proguardFiles para \'proguard-rules.pro\' nos dois")
        return False

    backup_path = path + ".bak"
    shutil.copyfile(path, backup_path)
    text = text.replace(old_block, new_block, 1)

    old_dep_line = "    implementation \'androidx.appcompat:appcompat:1.7.0\'\n"
    if old_dep_line in text:
        text = text.replace(old_dep_line, "", 1)
    else:
        print("AVISO: nao encontrei a linha da dependencia androidx.appcompat para remover.")
        print("Pode ser que ja tenha sido removida. Prosseguindo mesmo assim.")

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Atualizado: " + path + "  (backup em " + backup_path + ")")
    return True


def write_proguard_rules():
    path = "app/proguard-rules.pro"
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()
        if "com.android.music" in existing and "MediaSessionCompat" in existing:
            print("app/proguard-rules.pro ja existe e parece ser o mesmo arquivo. Pulei.")
            return True
        backup_path = path + ".bak"
        shutil.copyfile(path, backup_path)
        print("AVISO: app/proguard-rules.pro ja existia com conteudo diferente.")
        print("Backup salvo em " + backup_path + ". Vou SOBRESCREVER com as regras novas.")
    with open(path, "w", encoding="utf-8") as f:
        f.write(PROGUARD_RULES)
    print("Criado: " + path)
    return True


def main():
    check_repo_root()

    if already_applied():
        print("A reducao de tamanho ja parece estar aplicada (encontrei proguardFiles em app/build.gradle).")
        print("Nada a fazer no build.gradle. Conferindo proguard-rules.pro...")
        write_proguard_rules()
        return

    print("Aplicando reducao de tamanho do APK (remover appcompat nao usada + ligar R8)...")

    success = False
    if is_git_repo():
        print("Repo git detectado, tentando \'git apply\'...")
        success = try_git_apply()

    if not success:
        print("Aplicando build.gradle manualmente...")
        success = manual_apply_build_gradle()

    write_proguard_rules()

    if success:
        print()
        print("Concluido. Arquivos alterados/criados:")
        print("  - app/build.gradle  (appcompat removida, R8 ligado em release e debug)")
        print("  - app/proguard-rules.pro  (regras de keep para midia/AIDL/componentes do app)")
        print()
        print("Proximo passo: ./gradlew assembleDebug")
        print("Depois de instalar, TESTE a notificacao de midia (play/pause/next/prev,")
        print("lockscreen) antes de confiar no resultado -- R8 pode quebrar reflection")
        print("silenciosamente mesmo com build OK.")
        print()
        print("Para comparar o tamanho:")
        print("  ls -la app/build/outputs/apk/debug/*.apk")
        print("  unzip -l app/build/outputs/apk/debug/*.apk | grep classes.dex")
    else:
        print()
        print("Nao foi possivel aplicar tudo automaticamente em app/build.gradle.")
        print("Ajuste manualmente conforme o aviso acima. O proguard-rules.pro")
        print("ja foi criado/atualizado independente disso.")
        sys.exit(1)


if __name__ == "__main__":
    main()
