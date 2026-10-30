# Regras R8/ProGuard para o port do Music (AOSP Android 1.6 -> moderno).
#
# Java puro, sem androidx: o R8 só precisa preservar o que é acessado por
# nome (componentes do manifest e a interface AIDL).

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
