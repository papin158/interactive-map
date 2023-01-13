import streamlit as st
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, pxx


st.markdown(f'''
    <style>
        section[data-testid="stSidebar"] .css-ng1t4o {{width: 12rem;}}
        section[data-testid="stSidebar"] .css-1d391kg {{width: 12rem;}}
        section[data-testid="stSidebar"] .css-e1fqkh3o11 {{width: 550px; visibility: hidden;}}
        
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
    # div.css-1yy6isu.e16nr0p34 {width: 100%; color: grey; text-align: center;}
    style = """
    <style>
      section[data-testid="stSidebar"].css-1vencpc.e1fqkh3o11 {height: 80%; }
      div.css-1fcdlhc.e1s6o5jp0 {width: 22%; margin-left: auto;}
      div.streamlit-expanderHeader.st-ae.st-et.st-ag.st-ah.st-ai.st-aj.st-ck.st-bi.st-eu.st-ev.st-ew.st-ex.st-ey.st-ar.st-as.st-b6.st-b5.st-b3.st-bq.st-c6.st-ez.st-b4.st-f0.st-f1.st-f2.st-f3.st-f4{color: grey;}
      
      
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
        color="Gray",
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
        body,
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)
    with st.expander('О разработчике'):
        st.write('Сделано студентом ЗФ РАНХиГС Морозовым Денисом')


def footer():
    myargs = [
        "Создано с душой",
        #"Создано с душой ©ZF RANEPA ",
        #link("https://vk.com/gby2014", "@Papin158"),
        br(),
    ]
    layout(*myargs)
