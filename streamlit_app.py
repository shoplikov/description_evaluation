import streamlit as st
import json
from pathlib import Path

def load_json(uploaded_file):
    if uploaded_file is not None:
        content = uploaded_file.read().decode('utf-8')
        return json.loads(content)
    return None

def save_json(data, original_filename):
    output_filename = f"marked_{original_filename}"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return output_filename

def init_session_state(data, filename):
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'marked_data' not in st.session_state:
        st.session_state.marked_data = data.copy()
        for item in st.session_state.marked_data:
            item['mark'] = None
    if 'original_filename' not in st.session_state:
        st.session_state.original_filename = filename

def main():
    st.title("Оценка сокращенных описаний")
    
    uploaded_file = st.file_uploader("Выберите JSON-файл", type=['json'])
    
    if uploaded_file is not None:
        data = load_json(uploaded_file)
        if data is None:
            st.error("Пожалуйста, загрузите валидный JSON-файл")
            return
        
        init_session_state(data, uploaded_file.name)
        
        st.session_state.current_index = max(0, min(st.session_state.current_index, len(data) - 1))

        # Прогресс
        progress = (st.session_state.current_index + 1) / len(data)
        st.progress(progress)
        st.write(f"Дело {st.session_state.current_index + 1} из {len(data)}")

        col1, col2, col3 = st.columns([1, 2, 1])
       
        with col1:
            prev_disabled = st.session_state.current_index <= 0
            if st.button("← Предыдущий", disabled=prev_disabled):
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                    st.rerun()
                
        with col3:
            next_disabled = (st.session_state.current_index >= len(data) - 1) or \
                          (st.session_state.marked_data[st.session_state.current_index]['mark'] is None)
            if st.button("Следующий →", disabled=next_disabled):
                if st.session_state.current_index < len(data) - 1 and \
                   st.session_state.marked_data[st.session_state.current_index]['mark'] is not None:
                    st.session_state.current_index += 1
                    st.rerun()
        
        current_item = data[st.session_state.current_index]
        current_mark = st.session_state.marked_data[st.session_state.current_index]['mark']
        
        # Карточка
        with st.container():
            # Рейтинг
            st.markdown("### Оцените по 5-ти бальной шкале:")
            
            cols = st.columns(5)  # Changed to 5 columns for 1-5 scale
            
            for rating in range(1, 6):  # Changed to 1-5
                with cols[rating-1]:
                    button_style = "background-color: lightblue;" if current_mark == rating else ""
                    
                    if st.button(f"{rating}", key=f"rating_{rating}", 
                                 help=f"Оценка {rating}/5",
                                 type="primary" if current_mark == rating else "secondary"):
                        st.session_state.marked_data[st.session_state.current_index]['mark'] = rating
                        if st.session_state.current_index < len(data) - 1:
                            st.session_state.current_index += 1
                            st.rerun()     

            st.markdown("### Описание")
            st.write(current_item['description'])
            
            st.markdown("### Сокращенное описание")
            st.write(current_item['short_description'])
        
        # Проверка на все отмеченные
        all_marked = all(item['mark'] is not None for item in st.session_state.marked_data)
        
        if all_marked:
            st.success("Все карты отмечены. Сохраните результаты в JSON.")
            if st.button("Создать JSON-файл"):
                filename = save_json(st.session_state.marked_data, st.session_state.original_filename)
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="Скачать JSON-файл",
                        data=f,
                        file_name=filename,
                        mime="application/json"
                    )

if __name__ == "__main__":
    main()
