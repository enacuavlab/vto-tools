#Directories
SRC_DIR=/home/pprz/tmp2/mycamera2
OUT_DIR=/home/pprz/tmp2/mycamera2_thumb

EXTN="*.jpg"
SQ_EXTN=-sq.jpg
TH_EXTN=-th.jpg
2S_EXTN=-2s.jpg
SM_EXTN=-sm.jpg
ME_EXTN=-me.jpg
LA_EXTN=-la.jpg
XL_EXTN=-xl.jpg
XS_EXTN=-xs.jpg
XX_EXTN=-xx.jpg

SQUARE=120x120!

SRC_FILES = $(sort $(shell find $(SRC_DIR) -type f -name $(EXTN)))

IMG_SQ=$(patsubst $(SRC_DIR)/%.jpg,$(OUT_DIR)/%$(SQ_EXTN), $(SRC_FILES))
IMG_TH=$(patsubst $(SRC_DIR)/%.jpg,$(OUT_DIR)/%$(TH_EXTN), $(SRC_FILES))
IMG_2S=$(patsubst $(SRC_DIR)/%.jpg,$(OUT_DIR)/%$(2S_EXTN), $(SRC_FILES))
IMG_SM=$(patsubst $(SRC_DIR)/%.jpg,$(OUT_DIR)/%$(SM_EXTN), $(SRC_FILES))
IMG_ME=$(patsubst $(SRC_DIR)/%.jpg,$(OUT_DIR)/%$(ME_EXTN), $(SRC_FILES))
IMG_LA=$(patsubst $(SRC_DIR)/%.jpg,$(OUT_DIR)/%$(LA_EXTN), $(SRC_FILES))
IMG_XL=$(patsubst $(SRC_DIR)/%.jpg,$(OUT_DIR)/%$(XL_EXTN), $(SRC_FILES))
IMG_XS=$(patsubst $(SRC_DIR)/%.jpg,$(OUT_DIR)/%$(XS_EXTN), $(SRC_FILES))
IMG_XX=$(patsubst $(SRC_DIR)/%.jpg,$(OUT_DIR)/%$(XX_EXTN), $(SRC_FILES))

default: SQ TH 2S XS SM ME LA XL XX

SQ: $(IMG_SQ)
$(OUT_DIR)/%$(SQ_EXTN): $(SRC_DIR)/%.jpg  
	@convert $< -resize $(SQUARE) $@

TH: $(IMG_TH)
$(OUT_DIR)/%$(TH_EXTN): $(SRC_DIR)/%.jpg  
	@convert $< -resize 144x144 $@

2S: $(IMG_2S)
$(OUT_DIR)/%$(2S_EXTN): $(SRC_DIR)/%.jpg  
	@convert $< -resize 240x240 $@

XS: $(IMG_XS)
$(OUT_DIR)/%$(XS_EXTN): $(SRC_DIR)/%.jpg  
	@convert $< -resize 432x324 $@

SM: $(IMG_SM)
$(OUT_DIR)/%$(SM_EXTN): $(SRC_DIR)/%.jpg  
	@convert $< -resize 576x432 $@

ME: $(IMG_ME)
$(OUT_DIR)/%$(ME_EXTN): $(SRC_DIR)/%.jpg  
	@convert $< -resize 792x594 $@

LA: $(IMG_LA)
$(OUT_DIR)/%$(LA_EXTN): $(SRC_DIR)/%.jpg  
	@convert $< -resize 1008x756 $@

XL: $(IMG_XL)
$(OUT_DIR)/%$(XL_EXTN): $(SRC_DIR)/%.jpg  
	@convert $< -resize 1224x918 $@

XX: $(IMG_XX)
$(OUT_DIR)/%$(XX_EXTN): $(SRC_DIR)/%.jpg  
	@convert $< -resize 878x1242 $@
