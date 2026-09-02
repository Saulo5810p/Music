#!/usr/bin/env python3
"""
fix_compile_errors.py

Corrige os 4 problemas de compilação Java apontados pelo
`./gradlew clean assembleDebug`:

  1. IMediaPlaybackService / R.aidl.IBinder "cannot find symbol"
     -> o .aidl está em app/src/main/java/... mas o AGP moderno só
        compila AIDL colocado em app/src/main/aidl/...
        Correção: mover o arquivo para o diretório correto.

  2. TouchInterceptor.java: "cannot find symbol: variable mContext"
     -> o construtor recebe `Context context` mas nunca guarda num
        campo. Correção: adicionar `private Context mContext;` e
        atribuir no construtor.

  3. MusicUtils.java: "cannot find symbol: class MediaScanner"
     -> android.media.MediaScanner é uma classe interna do framework,
        nunca foi API pública, e sumiu do SDK moderno.
        Correção: substituir o uso por MediaMetadataRetriever,
        que é a API pública equivalente para extrair capa de álbum
        embutida no arquivo de áudio.

  4. MusicBrowserActivity.java e MusicPicker.java:
     "error: constant expression required" em `case R.id.xxx:`
     -> com android.nonTransitiveRClass=true (ativo no gradle.properties
        deste projeto), os R.id deixam de ser constantes em tempo de
        compilação, e switch/case sobre eles não compila mais.
        Correção: converter os switch(v.getId()) afetados para
        if/else if.

Faz backup (.bak) de cada arquivo antes de editar. Idempotente:
rodar de novo não duplica nem quebra nada (verifica antes de aplicar
cada correção).

Uso (dentro do Termux, na pasta do projeto Music):
  python fix_compile_errors.py
ou apontando o caminho do repo:
  python fix_compile_errors.py /caminho/para/Music
"""

import sys
import os
import re
import shutil

PKG_REL = os.path.join("com", "android", "music")


def backup(path):
    bak = path + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print(f"[+] Backup criado: {bak}")


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------
# 1. Mover o .aidl para app/src/main/aidl/com/android/music/
# ---------------------------------------------------------------------
def fix_aidl_location(base_dir):
    java_aidl = os.path.join(
        base_dir, "app", "src", "main", "java", PKG_REL, "IMediaPlaybackService.aidl"
    )
    aidl_dir = os.path.join(base_dir, "app", "src", "main", "aidl", PKG_REL)
    aidl_target = os.path.join(aidl_dir, "IMediaPlaybackService.aidl")

    if os.path.isfile(aidl_target):
        print(f"[=] AIDL já está no lugar certo: {aidl_target}")
        return False

    if not os.path.isfile(java_aidl):
        print(f"[!] Não encontrei {java_aidl} para mover. Pulando essa correção.")
        return False

    os.makedirs(aidl_dir, exist_ok=True)
    shutil.move(java_aidl, aidl_target)
    print(f"[+] AIDL movido: {java_aidl}\n    -> {aidl_target}")
    return True


# ---------------------------------------------------------------------
# 2. TouchInterceptor.java: adicionar campo mContext
# ---------------------------------------------------------------------
def fix_touch_interceptor(base_dir):
    path = os.path.join(
        base_dir, "app", "src", "main", "java", PKG_REL, "TouchInterceptor.java"
    )
    if not os.path.isfile(path):
        print(f"[!] Não encontrei {path}. Pulando.")
        return False

    content = read(path)

    if "private Context mContext;" in content:
        print("[=] TouchInterceptor.java já tem mContext declarado.")
        return False

    # Declara o campo logo após a abertura da classe
    class_decl_re = re.compile(r"(public class TouchInterceptor extends ListView\s*\{)")
    if not class_decl_re.search(content):
        print("[!] Não encontrei a declaração da classe TouchInterceptor. Pulando.")
        return False
    content = class_decl_re.sub(r"\1\n    private Context mContext;\n", content, count=1)

    # Atribui no construtor: cobre os dois construtores comuns
    # (Context) e (Context, AttributeSet)
    ctor_re = re.compile(
        r"(public TouchInterceptor\([^)]*Context context[^)]*\)\s*\{)"
    )

    def add_assignment(m):
        return m.group(1) + "\n        mContext = context;"

    new_content, n = ctor_re.subn(add_assignment, content)
    if n == 0:
        print("[!] Não encontrei construtor(es) com parâmetro Context em TouchInterceptor.java. "
              "Campo declarado, mas atribuição não inserida — revise manualmente.")
        write(path, content)
        return True

    backup(path)
    write(path, new_content)
    print(f"[+] mContext declarado e atribuído em {n} construtor(es) de {path}")
    return True


# ---------------------------------------------------------------------
# 3. MusicUtils.java: trocar MediaScanner por MediaMetadataRetriever
# ---------------------------------------------------------------------
def fix_media_scanner(base_dir):
    path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, "MusicUtils.java")
    if not os.path.isfile(path):
        print(f"[!] Não encontrei {path}. Pulando.")
        return False

    content = read(path)

    if "android.media.MediaScanner" not in content:
        print("[=] MusicUtils.java já não usa MediaScanner.")
        return False

    backup(path)

    # import
    content = content.replace(
        "import android.media.MediaScanner;",
        "import android.media.MediaMetadataRetriever;",
    )

    # uso: MediaScanner scanner = new MediaScanner(context);
    #      ...
    #      art = scanner.extractAlbumArt(fd);
    # Substitui pelo equivalente com MediaMetadataRetriever, que
    # trabalha direto com o Uri (não precisa mais do FileDescriptor
    # manual, mas mantemos o bloco try/finally do pfd por segurança
    # de compatibilidade com o resto do método).
    old_block = re.search(
        r"MediaScanner scanner = new MediaScanner\(context\);\s*"
        r"ParcelFileDescriptor pfd = null;\s*"
        r"try \{\s*"
        r"pfd = context\.getContentResolver\(\)\.openFileDescriptor\(uri, \"r\"\);\s*"
        r"if \(pfd != null\) \{\s*"
        r"FileDescriptor fd = pfd\.getFileDescriptor\(\);\s*"
        r"art = scanner\.extractAlbumArt\(fd\);\s*"
        r"\}\s*"
        r"\} catch \(IOException ex\) \{\s*"
        r"\} catch \(SecurityException ex\) \{\s*"
        r"\} finally \{\s*"
        r"try \{\s*"
        r"if \(pfd != null\) \{\s*"
        r"pfd\.close\(\);\s*"
        r"\}\s*"
        r"\} catch \(IOException ex\) \{\s*"
        r"\}\s*"
        r"\}",
        content,
    )

    new_block = (
        "MediaMetadataRetriever retriever = new MediaMetadataRetriever();\n"
        "                try {\n"
        "                    retriever.setDataSource(context, uri);\n"
        "                    byte[] artBytes = retriever.getEmbeddedPicture();\n"
        "                    if (artBytes != null) {\n"
        "                        art = BitmapFactory.decodeByteArray(artBytes, 0, artBytes.length);\n"
        "                    }\n"
        "                } catch (IllegalArgumentException ex) {\n"
        "                } catch (RuntimeException ex) {\n"
        "                } finally {\n"
        "                    try {\n"
        "                        retriever.release();\n"
        "                    } catch (RuntimeException ex) {\n"
        "                    }\n"
        "                }"
    )

    if old_block:
        content = content[: old_block.start()] + new_block + content[old_block.end() :]
        print("[+] Bloco MediaScanner.extractAlbumArt substituído por MediaMetadataRetriever.")
    else:
        print(
            "[!] Não encontrei o bloco exato de uso de MediaScanner para substituir "
            "automaticamente (só troquei o import). Revise manualmente o método "
            "getArtwork em MusicUtils.java — procure por 'scanner.extractAlbumArt'."
        )

    write(path, content)
    return True


# ---------------------------------------------------------------------
# 4. switch(v.getId()) -> if/else if em arquivos com R.id não-constante
# ---------------------------------------------------------------------
def convert_switch_to_if(content, switch_var="v.getId()"):
    """
    Converte um bloco:
        switch (v.getId()) {
            case R.id.a:
                ...
                break;
            case R.id.b:
                ...
                break;
        }
    em:
        int __id = v.getId();
        if (__id == R.id.a) {
            ...
        } else if (__id == R.id.b) {
            ...
        }
    Trabalha em nível de texto, assumindo indentação/formatação
    razoavelmente padrão (como no código deste repo).
    """
    switch_re = re.compile(
        r"switch\s*\(\s*" + re.escape(switch_var) + r"\s*\)\s*\{(.*?)\n(\s*)\}",
        re.DOTALL,
    )

    m = switch_re.search(content)
    if not m:
        return content, 0

    body = m.group(1)
    closing_indent = m.group(2)

    # Quebra em cases
    case_re = re.compile(r"case\s+(R\.id\.\w+)\s*:\s*(.*?)(?=(?:case\s+R\.id\.\w+\s*:)|\Z)", re.DOTALL)
    cases = case_re.findall(body)

    if not cases:
        return content, 0

    out_lines = [f"        int __clickedId = {switch_var};"]
    first = True
    for case_id, case_body in cases:
        case_body = case_body.strip()
        # remove um 'break;' final, se houver
        case_body = re.sub(r"break\s*;\s*$", "", case_body).strip()
        kw = "if" if first else "} else if"
        first = False
        out_lines.append(f"        {kw} (__clickedId == {case_id}) {{")
        for line in case_body.splitlines():
            out_lines.append("    " + line)
    out_lines.append("        }")

    new_block = "\n".join(out_lines)
    new_content = content[: m.start()] + new_block + content[m.end() :]
    return new_content, len(cases)


def fix_switch_files(base_dir):
    targets = [
        ("MusicBrowserActivity.java", "v.getId()"),
        ("MusicPicker.java", "v.getId()"),
    ]
    changed_any = False
    for filename, switch_var in targets:
        path = os.path.join(base_dir, "app", "src", "main", "java", PKG_REL, filename)
        if not os.path.isfile(path):
            print(f"[!] Não encontrei {path}. Pulando.")
            continue

        content = read(path)
        if "__clickedId" in content:
            print(f"[=] {filename} já foi convertido (switch -> if/else).")
            continue

        new_content, n = convert_switch_to_if(content, switch_var)
        if n == 0:
            print(f"[!] Não encontrei switch({switch_var}) com case R.id.* em {filename}. Pulando.")
            continue

        backup(path)
        write(path, new_content)
        print(f"[+] {filename}: switch convertido para if/else ({n} cases) sobre {switch_var}.")
        changed_any = True

    return changed_any


# ---------------------------------------------------------------------
def main():
    base_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    base_dir = os.path.abspath(base_dir)
    print(f"[i] Repositório alvo: {base_dir}\n")

    any_change = False
    print("--- 1/4: AIDL ---")
    any_change |= fix_aidl_location(base_dir)

    print("\n--- 2/4: TouchInterceptor mContext ---")
    any_change |= fix_touch_interceptor(base_dir)

    print("\n--- 3/4: MediaScanner -> MediaMetadataRetriever ---")
    any_change |= fix_media_scanner(base_dir)

    print("\n--- 4/4: switch(R.id) -> if/else ---")
    any_change |= fix_switch_files(base_dir)

    print()
    print("=" * 60)
    if any_change:
        print("Correções aplicadas. Agora rode no Termux:")
        print()
        print("  ./gradlew clean assembleDebug")
    else:
        print("Nada para corrigir (já estava tudo aplicado).")
    print()
    print("Se aparecerem NOVOS erros, me manda o log completo que eu sigo daqui.")
    print("=" * 60)


if __name__ == "__main__":
    main()
