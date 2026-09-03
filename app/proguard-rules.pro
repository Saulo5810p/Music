# Regras R8/ProGuard para o port do Music (AOSP Donut -> moderno).
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
