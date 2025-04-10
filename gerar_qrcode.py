import qrcode

# Conteúdo que será embutido no QR Code
conteudo = "qrplane://projeto-fake-001"

# Gerar o QR Code
qr = qrcode.make(conteudo)

# Salvar como imagem (pode abrir no navegador depois pra testar)
qr.save("qrcode_teste.png")

print("QR Code gerado: qrcode_teste.png")
