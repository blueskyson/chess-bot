from PIL import Image

#開啟照片
imageA = Image.open('sprites/board.png')
imageA = imageA.convert('RGBA')
widthA , heightA = imageA.size

#開啟簽名檔
imageB = Image.open('sprites/blackBishop.png')
imageB = imageB.convert('RGBA')
widthB , heightB = imageB.size

#新建一個透明的底圖
resultPicture = Image.new('RGBA', imageA.size, (0, 0, 0, 0))
#把照片貼到底圖
resultPicture.paste(imageA,(0,0))

#設定簽名檔的位置參數
pos = (30, 30, 80, 80)

#為了背景保留透明度，將im參數與mask參數皆帶入重設過後的簽名檔圖片
resultPicture.paste(imageB, pos, imageB)

#儲存新的照片
resultPicture.save("已合成圖片.png")