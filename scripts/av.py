"""Utilidades de áudio/vídeo: localiza o ffmpeg (do sistema ou do pacote imageio-ffmpeg) e mede duração sem ffprobe."""
import re, shutil, subprocess, sys

_FFMPEG = None

# Faixas que nunca entram como fundo dos Reels: sinos, carrilhões e gravações de campo do arquivo da
# Rádio Tcheca (série CRA…, que são sinos de igreja). Vale para a busca (fetch_music) e para a escolha (make_reel).
VETO_MUSICA = re.compile(r"\b(bells?|zvony?|sinos?|glocken?|gel[aä]ut\w*|campan\w*|carillon\w*|cloches?)\b|CRA\d{4,}", re.I)


def ffmpeg_bin():
    """Caminho do ffmpeg. Se não houver no sistema (ex.: imagem nova do runner), usa o binário do imageio-ffmpeg."""
    global _FFMPEG
    if _FFMPEG:
        return _FFMPEG
    exe = shutil.which("ffmpeg")
    if not exe:
        try:
            import imageio_ffmpeg
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "imageio-ffmpeg"], check=False)
            import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"  ffmpeg do sistema ausente; usando {exe}")
    _FFMPEG = exe
    return exe


def ff(*args):
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", *map(str, args)], check=True)


def duracao(arq):
    """Duração em segundos, lida do cabeçalho que o ffmpeg imprime (não depende de ffprobe)."""
    r = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(arq), "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", r.stderr)
    if not m:
        return 0.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)
