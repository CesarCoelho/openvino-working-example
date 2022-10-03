#!/bin/bash

source /opt/intel/openvino/bin/setupvars.sh

python3 img_adjustments.py \
	--model_xml model_img_adjustments.xml \
	--model_bin model_img_adjustments.bin \
	--input_tiles tiles \
	--output_tiles output_directory

