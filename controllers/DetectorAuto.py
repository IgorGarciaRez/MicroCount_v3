import cv2 as cv
import numpy as np
import math

SEMENTE_ALEATORIA = 12345

try:
    # Importações necessárias da Pillow (PIL)
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("----------------------------------------------------------------")
    print("ERRO: A biblioteca 'Pillow' e necessaria para salvar em PDF.")
    print("Por favor, instale-a no seu ambiente virtual:")
    print("pip install Pillow")
    print("----------------------------------------------------------------")
    Image = None
    ImageDraw = None
    ImageFont = None


def _white_balance_grayworld(img_bgr):
    """Gray-world WB (fallback caso xphoto não exista)."""
    img = img_bgr.astype(np.float32)
    avg = img.reshape(-1, 3).mean(axis=0)
    gray = avg.mean()
    scale = gray / (avg + 1e-6)
    img *= scale
    return np.clip(img, 0, 255).astype(np.uint8)


def _auto_white_balance(img_bgr):
    try:
        wb = cv.xphoto.createSimpleWB()
        wb.setInputMin(0.0);
        wb.setInputMax(255.0)
        return wb.balanceWhite(img_bgr)
    except Exception:
        return _white_balance_grayworld(img_bgr)


def _circularity(contour):
    area = cv.contourArea(contour)
    if area <= 0:
        return 0.0, area, 0.0
    per = cv.arcLength(contour, True)
    if per == 0:
        return 0.0, area, 0.0
    circ = 4.0 * math.pi * area / (per * per)
    return float(circ), float(area), float(per)


def _non_max_suppression(points, strengths, min_dist):
    """Remove centros muito próximos; mantém o de maior forca."""
    if not points:
        return []
    pts = np.array(points, dtype=np.float32)
    strengths = np.array(strengths, dtype=np.float32)
    order = strengths.argsort()[::-1]
    keep = []
    taken = np.zeros(len(points), np.bool_)
    for i in order:
        if taken[i]:
            continue
        keep.append(tuple(map(int, pts[i])))
        taken |= (np.linalg.norm(pts - pts[i], axis=1) < float(min_dist))
    return keep


def detectar_colonias(
        img_bgr,
        *,
        min_area=1,
        max_area=30000,
        dist_frac=0.10,
        min_circularidade=0.10,
        nms_frac=0.5,
        debug=False,
        salvar_pdf_em=None
):
    """
    Segmenta e retorna centros (x,y) das colônias no ROI da imagem.
    ... (docstring igual) ...
    """

    cv.setRNGSeed(SEMENTE_ALEATORIA)

    h, w = img_bgr.shape[:2]

    # Lista para guardar as PÁGINAS A4 prontas para o PDF
    lista_paginas_a4 = []

    # --- Nova Função Auxiliar para criar a página A4 ---
    def _criar_pagina_a4(label, img_pil):
        # Define tamanho A4 em pixels (a 72 DPI)
        A4_SIZE_PX = (595, 842)
        MARGIN_PX = 40

        # Cria a página em branco
        page = Image.new('RGB', A4_SIZE_PX, 'white')
        draw = ImageDraw.Draw(page)

        # Tenta carregar uma fonte. Falha suavemente para a padrão.
        try:
            # Fonte comum em Linux. Ajuste o caminho se necessário.
            font = ImageFont.truetype("DejaVuSans.ttf", 16)
        except IOError:
            font = ImageFont.load_default()  # Fonte padrão (pixelada)

        # 1. Desenha o Label (Título)
        text_pos = (MARGIN_PX, MARGIN_PX)
        draw.text(text_pos, label, font=font, fill='black')

        # 2. Redimensiona a Imagem
        # Calcula o espaço máximo disponível para a imagem
        text_bbox = draw.textbbox(text_pos, label, font=font)
        img_top_y = text_bbox[3] + 20  # Posição Y onde a imagem começa (abaixo do texto)

        max_img_w = A4_SIZE_PX[0] - (2 * MARGIN_PX)
        max_img_h = A4_SIZE_PX[1] - img_top_y - MARGIN_PX

        # Redimensiona a imagem (mantendo proporção) para caber no espaço
        img_pil.thumbnail((max_img_w, max_img_h), Image.LANCZOS)

        # 3. Centraliza e Cola a Imagem na Página
        img_paste_x = (A4_SIZE_PX[0] - img_pil.width) // 2
        img_paste_y = img_top_y

        page.paste(img_pil, (img_paste_x, img_paste_y))

        return page

    # --- Função auxiliar para adicionar imagens ao PDF ---
    def adicionar_passo_pdf(label, imagem_cv2):
        if salvar_pdf_em and Image:
            try:
                # Converte de cv2 (BGR ou Gray) para PIL (RGB)
                if len(imagem_cv2.shape) == 2:  # Se for Grayscale
                    img_rgb = cv.cvtColor(imagem_cv2, cv.COLOR_GRAY2RGB)
                else:  # Se for BGR
                    img_rgb = cv.cvtColor(imagem_cv2, cv.COLOR_BGR2RGB)

                img_pil = Image.fromarray(img_rgb)

                # Criar a página A4 completa com label e imagem
                pagina = _criar_pagina_a4(label, img_pil)
                lista_paginas_a4.append(pagina)
            except Exception as e:
                print(f"Erro ao preparar pagina do PDF para '{label}': {e}")

    # ----------------------------------------------------

    if salvar_pdf_em:
        adicionar_passo_pdf("0. Imagem Original", img_bgr)

    # pré-processamento
    img = _auto_white_balance(img_bgr)
    img = cv.GaussianBlur(img, (0, 0), 0.8)
    lab = cv.cvtColor(img, cv.COLOR_BGR2LAB)
    L, A, B = cv.split(lab)
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    L = clahe.apply(L)
    lab = cv.merge([L, A, B])

    if salvar_pdf_em:
        img_preproc = cv.cvtColor(lab, cv.COLOR_LAB2BGR)
        adicionar_passo_pdf("1. Imagem Pre-processada (WB + CLAHE)", img_preproc)

    # segmentação com K-means
    ab = lab[:, :, 1:3].reshape(-1, 2).astype(np.float32)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 20, 0.5)
    _, labels, centers = cv.kmeans(ab, K=2, bestLabels=None, criteria=criteria,
                                   attempts=3, flags=cv.KMEANS_PP_CENTERS)
    labels = labels.reshape(h, w)
    means_L = [float(L[labels == i].mean()) if np.any(labels == i) else 255.0 for i in range(2)]
    obj_lab = int(np.argmin(means_L))
    mask = (labels == obj_lab).astype(np.uint8) * 255

    if salvar_pdf_em:
        adicionar_passo_pdf("2. Mascara K-Means", mask)

    # limpeza morfológica
    k3 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))
    k5 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, k3, iterations=1)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, k5, iterations=1)

    if salvar_pdf_em:
        adicionar_passo_pdf("3. Mascara Apos Limpeza Morfologica", mask)

    # remove partículas muito pequenas/grandes
    num, lbl, stats, _ = cv.connectedComponentsWithStats(mask, connectivity=8)
    mask_clean = np.zeros_like(mask)
    for i in range(1, num):
        area = int(stats[i, cv.CC_STAT_AREA])
        if min_area <= area <= max_area:
            mask_clean[lbl == i] = 255
    mask = mask_clean

    if mask.sum() == 0:
        return ([], {"mask": mask} if debug else [])

    # marcadores com distance transform
    dist = cv.distanceTransform(mask, cv.DIST_L2, 5)

    if salvar_pdf_em:
        dist_vis = cv.normalize(dist, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
        adicionar_passo_pdf("4. Transformada da Distancia", dist_vis)

    dist_blur = cv.GaussianBlur(dist, (0, 0), 1.0)
    maxv = dist_blur.max()
    if maxv <= 1e-6:
        return ([], {"mask": mask} if debug else [])

    dil = cv.dilate(dist_blur, k3)
    peaks = (dist_blur == dil) & (dist_blur > dist_frac * maxv)
    sure_fg = (peaks.astype(np.uint8) * 255)
    sure_fg = cv.dilate(sure_fg, k3, iterations=1)

    if salvar_pdf_em:
        adicionar_passo_pdf("5. Picos (Marcadores para Watershed)", sure_fg)

    # fundo certo e região desconhecida
    sure_bg = cv.dilate(mask, cv.getStructuringElement(cv.MORPH_ELLIPSE, (9, 9)), iterations=1)
    unknown = cv.subtract(sure_bg, sure_fg)

    gx = cv.Sobel(L, cv.CV_32F, 1, 0, ksize=3)
    gy = cv.Sobel(L, cv.CV_32F, 0, 1, ksize=3)
    grad = cv.magnitude(gx, gy)
    grad_u8 = cv.normalize(grad, None, 0, 255, cv.NORM_MINMAX).astype(np.uint8)
    grad_rgb = cv.cvtColor(grad_u8, cv.COLOR_GRAY2BGR)

    _, markers = cv.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    markers = cv.watershed(grad_rgb, markers)

    mask_final = (markers > 1).astype(np.uint8) * 255

    if salvar_pdf_em:
        markers_color = np.zeros((h, w, 3), dtype=np.uint8)
        for i in range(2, markers.max() + 1):
            markers_color[markers == i] = np.random.randint(50, 256, (3), dtype=np.uint8)
        markers_color[markers == -1] = (255, 255, 255)
        adicionar_passo_pdf("6. Resultado do Watershed", markers_color)

    # filtra por área e circularidade; extrai centros
    cnts, _ = cv.findContours(mask_final, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    centros = []
    strengths = []
    radii = []

    for c in cnts:
        circ, area, _ = _circularity(c)
        if area < min_area or area > max_area:
            continue
        if circ < min_circularidade:
            continue
        M = cv.moments(c)
        if M["m00"] == 0:
            continue
        cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
        centros.append((cx, cy))
        strengths.append(float(dist_blur[min(cy, h - 1), min(cx, w - 1)]))
        radii.append(strengths[-1])

    if radii:
        med_r = float(np.median(radii))
        min_sep = max(2.0, nms_frac * med_r * 2.0)
        centros = _non_max_suppression(centros, strengths, min_sep)

    if salvar_pdf_em:
        img_resultado = img_bgr.copy()
        for (cx, cy) in centros:
            cv.circle(img_resultado, (cx, cy), 10, (0, 255, 0), 2)
            cv.circle(img_resultado, (cx, cy), 1, (0, 0, 255), 2)

        cv.putText(img_resultado, f"Total: {len(centros)}", (10, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        adicionar_passo_pdf("7. Resultado Final", img_resultado)

    # --- Salva o PDF no final ---
    if salvar_pdf_em and lista_paginas_a4 and Image:
        try:
            # Pega a primeira página
            img1 = lista_paginas_a4[0]
            # Pega o resto das páginas
            outras_imgs = lista_paginas_a4[1:]

            # Salva a primeira página, anexando as outras
            img1.save(
                salvar_pdf_em,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=outras_imgs
            )
            print(f"PDF A4 com {len(lista_paginas_a4)} passos salvo em: {salvar_pdf_em}")
        except Exception as e:
            print(f"ERRO ao salvar o PDF: {e}")
    # ----------------------------

    if debug:
        dbg = {
            "mask_kmeans": mask,
            "dist": cv.normalize(dist, None, 0, 255, cv.NORM_MINMAX).astype(np.uint8),
            "peaks": sure_fg,
            "mask_final": mask_final,
            "grad": grad_u8,
        }
        return centros, dbg
    return centros