from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Abrir imagem original
img = Image.open("Gemini_Generated_Image_qoavbfqoavbfqoav.png").convert("RGBA")
data = np.array(img)

# Tornar fundo quadriculado claro totalmente transparente
r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
mask = (r > 200) & (g > 200) & (b > 200)
data[mask] = [255, 255, 255, 0]
transparent_img = Image.fromarray(data)

# Criar nova imagem transparente para redesenhar texto em branco
new_img = Image.new("RGBA", transparent_img.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(new_img)

# Tamanhos aproximados para as fontes
width, height = new_img.size
font_crte = ImageFont.truetype("arialbd.ttf", int(height * 0.25))    # Fonte "CRTE"
font_suporte = ImageFont.truetype("arial.ttf", int(height * 0.13))   # Fonte "Suporte"
font_toledo = ImageFont.truetype("arial.ttf", int(height * 0.07))    # Fonte "Toledo"

# Textos
text1 = "CRTE"
text2 = "Suporte"
text3 = "Toledo"

# Centralizar e posicionar os textos verticalmente
text1_w, text1_h = draw.textsize(text1, font=font_crte)
text2_w, text2_h = draw.textsize(text2, font=font_suporte)
text3_w, text3_h = draw.textsize(text3, font=font_toledo)

total_height = text1_h + text2_h + text3_h + 20
start_y = (height - total_height) // 2

draw.text(((width - text1_w) // 2, start_y), text1, font=font_crte, fill="white")
draw.text(((width - text2_w) // 2, start_y + text1_h + 5), text2, font=font_suporte, fill="white")
draw.text(((width - text3_w) // 2, start_y + text1_h + text2_h + 10), text3, font=font_toledo, fill="white")

# Salvar a imagem final
new_img.save("saida_final.png")
