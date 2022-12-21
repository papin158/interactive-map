import streamlit as st
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, pxx


st.set_page_config(page_title="Карта", layout="wide")

st.markdown(f'''
    <style>
        section[data-testid="stSidebar"] .css-ng1t4o {{width: 12rem;}}
        section[data-testid="stSidebar"] .css-1d391kg {{width: 12rem;}}

        footer{{visibility: visible;}}
        footer:after
        {{
            content: 'Создано с душой ©ZF RANEPA';
            display: block;
            position: relative;
            padding: 5px;
            top: 3px;
        }}
    </style>
''', unsafe_allow_html=True)


def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):
    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
    </style>
    """

    style_div = styles(
        position="relative",
        left=0,
        bottom=0,
        margin=pxx(0, 0, 0, 0),
        width=percent(100),
        color="red",
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        display="block",
        margin=pxx(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=pxx(2)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = [
        "Создано с душой ©ZF RANEPA ",
        #link("https://vk.com/gby2014", "@Papin158"),
        br(),
    ]
    layout(*myargs)
