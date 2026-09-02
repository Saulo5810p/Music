#!/usr/bin/env python3
"""
fix_aidl_arch.py

Corrige o erro:
  Task :app:compileDebugAidl FAILED
  .../build-tools/34.0.0/aidl: 6: Syntax error: Unterminated quoted string

Causa raiz: o `aidl` que vem dentro do android-sdk (pacote
lzhiyong/termux-ndk, usado com box64/glibc-runner) é um binário
x86-64, mas o seu dispositivo (Samsung Galaxy A35) é aarch64/ARM.
O binário não roda de verdade; o que sobra é interpretado errado
pelo shell, gerando o "Unterminated quoted string".

É o mesmo problema que aapt2 tem nesse mesmo pacote (documentado
oficialmente pelo autor do termux-ndk), e a solução é a mesma
ideia que você já usa para aapt2 via android.aapt2FromMavenOverride:
usar o binário NATIVO aarch64.

Só que aidl não tem uma flag "FromMavenOverride" equivalente no
Gradle -- o caminho é fixo em
  <sdk>/build-tools/<versão>/aidl
Então a correção é: instalar o pacote `aidl` nativo do Termux
(pkg install aidl, aarch64 de verdade) e SUBSTITUIR o binário
x86-64 dentro do android-sdk por esse, mantendo o mesmo caminho
que o Gradle já espera. Assim não precisa mexer no build.gradle.

O script:
  1. Verifica se o pacote `aidl` do Termux está instalado
     (instala via `pkg install -y aidl` se não estiver).
  2. Localiza o aidl nativo (normalmente em $PREFIX/bin/aidl).
  3. Localiza o(s) aidl x86-64 dentro do android-sdk/build-tools/*/.
  4. Faz backup do binário original (.bak) e substitui por um
     link simbólico para o aidl nativo.
  5. É idempotente.

Uso (dentro do Termux):
  python fix_aidl_arch.py
Opcional -- apontar manualmente o SDK se não estiver em
$HOME/android-sdk:
  python fix_aidl_arch.py /caminho/para/android-sdk
"""

import sys
import os
import glob
import shutil
import subprocess

def sh(cmd, check=True):
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, text=True,
                             capture_output=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    if check and result.returncode != 0:
        raise RuntimeError(f"Comando falhou (exit {result.returncode}): {cmd}")
    return result


def find_termux_prefix():
    prefix = os.environ.get("PREFIX")
    if prefix and os.path.isdir(prefix):
        return prefix
    fallback = "/data/data/com.termux/files/usr"
    if os.path.isdir(fallback):
        return fallback
    return None


def ensure_native_aidl(prefix):
    native_aidl = os.path.join(prefix, "bin", "aidl")
    if os.path.isfile(native_aidl):
        print(f"[=] aidl nativo já instalado: {native_aidl}")
        return native_aidl

    print("[i] Pacote 'aidl' não encontrado. Instalando via pkg...")
    sh("pkg install -y aidl", check=True)

    if os.path.isfile(native_aidl):
        print(f"[+] aidl nativo instalado: {native_aidl}")
        return native_aidl

    raise FileNotFoundError(
        f"Instalei o pacote mas não achei o binário em {native_aidl}. "
        "Rode `pkg install aidl` manualmente e me mande o output."
    )


def find_sdk_dir(base_arg):
    if base_arg:
        candidate = os.path.abspath(base_arg)
        if os.path.isdir(candidate):
            return candidate
        raise FileNotFoundError(f"{candidate} não existe.")

    home = os.path.expanduser("~")
    candidate = os.path.join(home, "android-sdk")
    if os.path.isdir(candidate):
        return candidate

    # fallback: procura em locais comuns
    for guess in [
        os.path.join(home, "Android", "sdk"),
        os.path.join(home, ".android-sdk"),
    ]:
        if os.path.isdir(guess):
            return guess

    raise FileNotFoundError(
        "Não encontrei o android-sdk automaticamente. Rode o script passando "
        "o caminho: python fix_aidl_arch.py /caminho/para/android-sdk"
    )


def patch_sdk_aidl_binaries(sdk_dir, native_aidl):
    pattern = os.path.join(sdk_dir, "build-tools", "*", "aidl")
    matches = glob.glob(pattern)

    if not matches:
        print(f"[!] Nenhum binário aidl encontrado em {pattern}")
        return 0

    patched = 0
    for path in matches:
        if os.path.islink(path):
            target = os.readlink(path)
            if target == native_aidl:
                print(f"[=] {path} já aponta para o aidl nativo.")
                continue

        backup = path + ".x86_64.bak"
        if not os.path.exists(backup) and not os.path.islink(path):
            shutil.copy2(path, backup)
            print(f"[+] Backup do binário original: {backup}")
        elif os.path.islink(path):
            # já era um link (de outra correção anterior) -- remove antes de recriar
            pass

        if os.path.islink(path) or os.path.isfile(path):
            os.remove(path)

        os.symlink(native_aidl, path)
        os.chmod(native_aidl, 0o755)
        print(f"[+] {path} agora é um symlink para {native_aidl}")
        patched += 1

    return patched


def main():
    base_arg = sys.argv[1] if len(sys.argv) > 1 else None

    prefix = find_termux_prefix()
    if not prefix:
        print("[!] Não parece que este script está rodando dentro do Termux "
              "(variável $PREFIX não encontrada). Rode-o no Termux.")
        sys.exit(1)

    print(f"[i] Termux PREFIX: {prefix}")

    try:
        native_aidl = ensure_native_aidl(prefix)
    except Exception as e:
        print(f"[!] Erro: {e}")
        sys.exit(1)

    try:
        sdk_dir = find_sdk_dir(base_arg)
    except Exception as e:
        print(f"[!] Erro: {e}")
        sys.exit(1)

    print(f"[i] android-sdk: {sdk_dir}")

    n = patch_sdk_aidl_binaries(sdk_dir, native_aidl)

    print()
    print("=" * 60)
    if n > 0:
        print(f"{n} binário(s) aidl substituído(s) pelo nativo aarch64.")
    else:
        print("Nada para trocar (já estava tudo certo).")
    print()
    print("Agora rode, na pasta do projeto Music:")
    print()
    print("  ./gradlew clean assembleDebug")
    print("=" * 60)


if __name__ == "__main__":
    main()
