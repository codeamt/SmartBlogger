# UI-Specific Discussion

We don't  seem to be using shadcn as we should. Here's more insight on how to integrate:

**`streamlit-shadcn-ui Basic Usage:`**

import the library and start using components in your Streamlit application.

```python
import streamlit as st
from streamlit_shadcn_ui import ui

st.set_page_config(layout="wide")

st.title("Streamlit Shadcn UI Demo")

# Example: Button
if ui.button("Click Me", key="my_button", variant="default"):
    st.success("Button clicked!")

# Example: Input
user_input = ui.input(placeholder="Enter text...", key="my_input")
st.write(f"You entered: {user_input}")

# Example: Checkbox
checked = ui.checkbox("Agree to terms", key="my_checkbox")
st.write(f"Checkbox status: {checked}")
```

---

`Using Different Components:`

Explore various components available in streamlit-shadcn-ui, such as:

cards:

```python
with ui.card(key="my_card"):
    st.subheader("This is a Card")
    st.write("Content inside the card.")
```

tabs:

```python
with ui.tabs(default_value="tab1", key="my_tabs") as tabs:
    with tabs.tab_item("Tab 1", key="tab1"):
        st.write("Content for Tab 1")
  
    with tabs.tab_item("Tab 2", key="tab2"):
        st.write("Content for Tab 2")
```

select:

```python
selected_option = ui.select(options=["Option A", "Option B", "Option C"], default_value="Option A", key="my_select")
st.write(f"Selected: {selected_option}")
```

table:

```python
import pandas as pd

data = pd.DataFrame({"Name": ["Alice", "Bob"], "Age": [30, 24]})
ui.table(data, key="my_table")
```

---

`Nesting Components (Advanced):`

The library supports nesting components within each other for more complex layouts.

```python
with ui.card(key="outer_card"):
    st.subheader("Outer Card")
      
with ui.card(key="inner_card"):
    st.write("Content in inner card")
    ui.button("Inner Button", key="inner_btn")
```

`Examples using streamlit-shadcn-ui:`

[https://shadcn.streamlit.app/](https://shadcn.streamlit.app/)

[https://github.com/antoineross/streamlit-saas-starter](https://github.com/antoineross/streamlit-saas-starter)

---

### An example custom theme:

```css
:root {
  --background: hsl(0 0% 100%);
  --foreground: hsl(240 10% 3.9%);
  --card: hsl(0 0% 100%);
  --card-foreground: hsl(240 10% 3.9%);
  --popover: hsl(0 0% 100%);
  --popover-foreground: hsl(240 10% 3.9%);
  --primary: hsl(240 5.9% 10%);
  --primary-foreground: hsl(0 0% 98%);
  --secondary: hsl(240 4.8% 95.9%);
  --secondary-foreground: hsl(240 5.9% 10%);
  --muted: hsl(240 4.8% 95.9%);
  --muted-foreground: hsl(240 3.8% 46.1%);
  --accent: hsl(240 4.8% 95.9%);
  --accent-foreground: hsl(240 5.9% 10%);
  --destructive: hsl(0 84.2% 60.2%);
  --destructive-foreground: hsl(0 0% 98%);
  --border: hsl(240 5.9% 90%);
  --input: hsl(240 5.9% 90%);
  --ring: hsl(240 5.9% 10%);
  --chart-1: hsl(200 60% 70%);
  --chart-2: hsl(100 60% 70%);
  --chart-3: hsl(300 60% 70%);
  --chart-4: hsl(40 60% 70%);
  --chart-5: hsl(280 60% 70%);
  --sidebar: hsl(240 10% 3.9%);
  --sidebar-foreground: hsl(0 0% 98%);
  --sidebar-primary: hsl(0 0% 98%);
  --sidebar-primary-foreground: hsl(240 5.9% 10%);
  --sidebar-accent: hsl(240 4.8% 95.9%);
  --sidebar-accent-foreground: hsl(240 5.9% 10%);
  --sidebar-border: hsl(240 5.9% 90%);
  --sidebar-ring: hsl(240 5.9% 10%);
  --radius: 0.5rem;
  --shadow-color: hsl(240 5.9% 10%);
  --shadow-opacity: 0.1;
  --shadow-blur: 10px;
  --shadow-spread: 0px;
  --shadow-offset-x: 0px;
  --shadow-offset-y: 4px;
  --letter-spacing: 0em;
  /* Fonts will need to be configured separately in your application's font loading mechanism. */
  /* For example, in Streamlit, you might use st.markdown with a <style> tag to import fonts. */
  /* --font-sans: 'Inter', sans-serif; */
  /* --font-serif: 'Playfair Display', serif; */
  /* --font-mono: 'Fira Code', monospace; */
}

.dark {
  --background: hsl(240 10% 3.9%);
  --foreground: hsl(0 0% 98%);
  --card: hsl(240 10% 3.9%);
  --card-foreground: hsl(0 0% 98%);
  --popover: hsl(240 10% 3.9%);
  --popover-foreground: hsl(0 0% 98%);
  --primary: hsl(0 0% 98%);
  --primary-foreground: hsl(240 5.9% 10%);
  --secondary: hsl(240 3.7% 15.9%);
  --secondary-foreground: hsl(0 0% 98%);
  --muted: hsl(240 3.7% 15.9%);
  --muted-foreground: hsl(240 5% 64.9%);
  --accent: hsl(240 3.7% 15.9%);
  --accent-foreground: hsl(0 0% 98%);
  --destructive: hsl(0 62.8% 30.6%);
  --destructive-foreground: hsl(0 0% 98%);
  --border: hsl(240 3.7% 15.9%);
  --input: hsl(240 3.7% 15.9%);
  --ring: hsl(240 4.9% 83.9%);
  --chart-1: hsl(200 60% 50%);
  --chart-2: hsl(100 60% 50%);
  --chart-3: hsl(300 60% 50%);
  --chart-4: hsl(40 60% 50%);
  --chart-5: hsl(280 60% 50%);
  --sidebar: hsl(0 0% 98%);
  --sidebar-foreground: hsl(240 10% 3.9%);
  --sidebar-primary: hsl(240 5.9% 10%);
  --sidebar-primary-foreground: hsl(0 0% 98%);
  --sidebar-accent: hsl(240 3.7% 15.9%);
  --sidebar-accent-foreground: hsl(0 0% 98%);
  --sidebar-border: hsl(240 3.7% 15.9%);
  --sidebar-ring: hsl(240 4.9% 83.9%);
  --radius: 0.5rem;
  --shadow-color: hsl(0 0% 98%);
  --shadow-opacity: 0.05;
  --shadow-blur: 8px;
  --shadow-spread: 0px;
  --shadow-offset-x: 0px;
  --shadow-offset-y: 3px;
  --letter-spacing: 0em;
  /* Fonts will need to be configured separately in your application's font loading mechanism. */
  /* For example, in Streamlit, you might use st.markdown with a <style> tag to import fonts. */
  /* --font-sans: 'Inter', sans-serif; */
  /* --font-serif: 'Playfair Display', serif; */
  /* --font-mono: 'Fira Code', monospace; */
}
```

Helpful Libraries:

```bash
uv add streamlit-pills
uv add streamlit-on-Hover-tabs
uv add streamlit-custom-sidebar
```

`streamlit-pills example`:

```python
import streamkit as st 
from streamlit_pills import pills 

selected = pills("Label", ["Option 1", "Option 2", "Option 3"], ["🍀", "🎈", "🌈"])
st.write(selected)
```

`streamlit-on-Hover-tabs`:

```python
from st_on_hover_tabs import on_hover_tabs
import streamlit as st
st.set_page_config(layout="wide")

st.header("Custom tab component for on-hover navigation bar")
st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

with st.sidebar:
    tabs = on_hover_tabs(tabName=['Dashboard', 'Money', 'Economy'], 
                         iconName=['dashboard', 'money', 'economy'], default_choice=0)

if tabs =='Dashboard':
    st.title("Navigation Bar")
    st.write('Name of option is {}'.format(tabs))

elif tabs == 'Money':
    st.title("Paper")
    st.write('Name of option is {}'.format(tabs))

elif tabs == 'Economy':
    st.title("Tom")
    st.write('Name of option is {}'.format(tabs))
  
```

```python
with st.sidebar:
        tabs = on_hover_tabs(tabName=['Dashboard', 'Money', 'Economy'], 
                             iconName=['dashboard', 'money', 'economy'],
                             styles = {'navtab': {'background-color':'#111',
                                                  'color': '#818181',
                                                  'font-size': '18px',
                                                  'transition': '.3s',
                                                  'white-space': 'nowrap',
                                                  'text-transform': 'uppercase'},
                                       'tabStyle': {':hover :hover': {'color': 'red',
                                                                      'cursor': 'pointer'}},
                                       'tabStyle' : {'list-style-type': 'none',
                                                     'margin-bottom': '30px',
                                                     'padding-left': '30px'},
                                       'iconStyle':{'position':'fixed',
                                                    'left':'7.5px',
                                                    'text-align': 'left'},
                                       },
                             key="1")
```

`streamlit-custom-sidebar example`:

```toml
# Pre-requisites

#create `.streamlit/config.toml` directory where the main app.py file is located in there, input 
[client]
showSidebarNavigation = false

```

```python
import streamlit as st
from streamlit_custom_sidebar import CustomSidebarDefault
import streamlit_float # recommended

# Note - on the page's first load - when user comes in from the url rather than clicking on the tab, the active page will be derived from the url or from the `loadPageName` parameter. Please make sure all params in the data array object are inputed.

st.set_page_config(layout="wide")

streamlit_float.float_init(include_unstable_primary=False)

#if the rendering gets too buggy that you don't feel comfortable, a simple time.sleep(2) helps after this component.
time.sleep(2) # optional

data_ = [
            {"index":0, "label":"Example", "page":"example", "href":"<http://localhost:8501/>"},
            {"index":1, "label":"Page", "page":"page", "icon":"ri-logout-box-r-line", "href":"<http://localhost:8501/page>"}
        ]

if "currentPage" not in st.session_state: # required as component will be looking for this in session state to change page via `switch_page`
    st.session_state["currentPage"] = data_[0] 
else:
    st.session_state["currentPage"] = data_[0] 

with st.container():
    defaultSidebar = CustomSidebarDefault(closeNavOnLoad=False, backgroundColor="brown", loadPageName="example", data=data_, LocalOrSessionStorage=1, serverRendering=False, webMedium="local") 
    defaultSidebar.load_custom_sidebar()
    defaultSidebar.change_page()
  
    streamlit_float.float_parent(css="position:fixed; top:-1000px;") # gets rid of the whitespace created from the iframes used to build the component - no big forehead.

# The above must be rendered atop every streamlit page

```

[https://www.datacamp.com/tutorial/deepseek-ocr-hands-on-guide](https://www.datacamp.com/tutorial/deepseek-ocr-hands-on-guide)
