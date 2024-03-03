from datetime import datetime, date
import requests
import random
import streamlit as st
from urllib.parse import quote_plus
from PIL import Image

PLACEHOLDER = "https://placehold.co/1000x1000"
IMAGEKIT_BASE_URL = "https://ik.imagekit.io"
OPTIONS_FONT = [
    "AbrilFatFace", "Amaranth", "Arvo", "Audiowide", "Chivo", "Crimson Text",
    "exo", "Fredoka One", "Gravitas One", "Kanit", "Lato", "Lobster",
    "Lora", "Monoton", "Montserrat", "PT Mono", "PT_Serif", "Open Sans",
    "Roboto", "Old Standard", "Ubuntu", "Vollkorn"
]
OPTIONS_RELATIVE_FOCUS = ["center", "top", "right", "bottom", "left", "top_left", "top_right", "bottom_left", "bottom_right"]

def get_query_param(key, default=""):
    return st.query_params.get(key, default)

def validate_access(access_token, imagekit_id):
    return access_token == st.secrets["ACCESS_TOKEN"] and imagekit_id == st.secrets["IMAGEKIT_ID"]

def main():
    access_token = get_query_param("access_token")
    imagekit_id = get_query_param("imagekit_id")

    if not access_token or not validate_access(access_token, imagekit_id):
        st.error("Invalid access_token or imagekit_id")
        return

    st.set_page_config(layout="wide")

    query_parma_path = st.query_params["path"] if "path" in st.query_params else ""

    default_url = st.query_params["url"] if "url" in st.query_params else PLACEHOLDER

    path = st.sidebar.text_input('Enter image path', key="path", value=query_parma_path)

    origin_image = f"{IMAGEKIT_BASE_URL}/{imagekit_id}/{path}"

    try:
        response = requests.get(origin_image, stream=True)
        if response.status_code == 200:
            response.raw.decode_content = True
            image = Image.open(response.raw)
            st.subheader(f"Image detail: {image.width} x {image.height} pixels")
        else:
            st.error(f"Failed to retrieve original image, status code: {response.status_code}")
    except Exception as e:
        st.error(f"An error occurred while fetching the original image size: {e}")

    tr_transformations = []

    resize_width = st.sidebar.slider('tr resize width', 200, 3000, 1000, step=10)
    resize_height = st.sidebar.slider('tr reize height', 200, 3000, 1000, step=10)

    tr_transformations.append(f"w-{resize_width}")
    tr_transformations.append(f"h-{resize_height}")
    tr_transformations.append("cm-extract")

    method = st.sidebar.selectbox('method', options=["relative focus", "extract"], index=0)

    if method == "relative focus":
        relative_focus = st.sidebar.selectbox('relative focus', options=OPTIONS_RELATIVE_FOCUS, index=0)
        tr_transformations.append(f"fo-{relative_focus}")

    if method == "extract":
        position_x = st.sidebar.slider('tr position x', 0, 5000, step=10)
        position_y = st.sidebar.slider('tr position y', 0, 5000, step=10)

        tr_transformations.append(f"xc-{position_x}")
        tr_transformations.append(f"yc-{position_y}")

    rt_transformations = []

    st.sidebar.divider()

    resize_width = st.sidebar.slider('rt resize width', 200, 3000, 1000, step=10)
    resize_height = st.sidebar.slider('rt reize height', 200, 3000, 1000, step=10)
    rt_transformations.append(f"w-{resize_width}")
    rt_transformations.append(f"h-{resize_height}")

    format = st.sidebar.selectbox('format', options=["jpg", "png", "webp", "avif", "auto"], index=0)

    is_e_contrast = st.sidebar.toggle('add e contrast', key="is_e_contrast", value=True)

    if is_e_contrast:
        rt_transformations.append("e-contrast")

    is_e_sharpen = st.sidebar.toggle('add e sharpen', key="is_e_sharpen", value=True)

    if is_e_sharpen:
        rt_transformations.append("e-sharpen")

    is_text = st.sidebar.toggle('add text', key="is_text", value=False)

    overlay_text = ""

    if is_text:
        st.sidebar.caption("text:")
        text_lx = st.sidebar.number_input('position X', 0, 5000, 10, step=10)
        text_ly = st.sidebar.number_input('position Y', 0, 5000, 10, step=10)

        text = st.sidebar.text_input('text', value="default")
        text_encoded = quote_plus(text)

        text_color = st.sidebar.color_picker('color', '#000000')
        text_color_without_hash = text_color.lstrip('#')

        text_font = st.sidebar.selectbox('font', OPTIONS_FONT, index=0)

        overlay_text = f":l-text,i-{text_encoded},lx-{text_lx},ly-{text_ly},ff-{text_font},co-{text_color_without_hash},fs-45,l-end"

        st.sidebar.divider()

    rt_transformations.append(f"f-{format}")

    if path:
        col1, col2 = st.columns(2)

        tr_transformations = ",".join(tr_transformations)
        rt_transformations = ",".join(rt_transformations)

        src = f"{IMAGEKIT_BASE_URL}/{imagekit_id}/{path}?tr={tr_transformations}:{rt_transformations}"
        src =  src + overlay_text if is_text else src
        download_link = src + f"&ik-attachment=true"

        col1.subheader("Modifiy Image")
        col1.caption(src)
        col1.image(src, use_column_width="never", width=resize_width)

        col2.subheader("Original Image")
        col2.caption(origin_image)
        col2.image(origin_image, use_column_width="never")

        st.sidebar.link_button("Download Image", download_link)


if __name__ == '__main__':
  main()
