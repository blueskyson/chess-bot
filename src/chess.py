from PIL import Image

#開啟照片
imageA = Image.open('範例圖片C.jpg')
imageA = imageA.convert('RGBA')
widthA , heightA = imageA.size

#開啟簽名檔
imageB = Image.open('mySign.png')
imageB = imageB.convert('RGBA')
widthB , heightB = imageB.size

#重設簽名檔的寬為照片的1/2
newWidthB = int(widthA/2)
#重設簽名檔的高依據新的寬度等比例縮放
newHeightB = int(heightB/widthB*newWidthB)
#重設簽名檔圖片
imageB_resize = imageB.resize((newWidthB, newHeightB))

#新建一個透明的底圖
resultPicture = Image.new('RGBA', imageA.size, (0, 0, 0, 0))
#把照片貼到底圖
resultPicture.paste(imageA,(0,0))

#設定簽名檔的位置參數
right_bottom = (widthA - newWidthB, heightA - newHeightB)

#為了背景保留透明度，將im參數與mask參數皆帶入重設過後的簽名檔圖片
resultPicture.paste(imageB_resize, right_bottom, imageB_resize)

#儲存新的照片
resultPicture.save("已合成圖片.png")