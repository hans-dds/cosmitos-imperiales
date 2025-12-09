import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from infrastructure.ui.components.word_cloud_component import WordCloudComponent

@pytest.fixture
def mock_streamlit():
    with patch('infrastructure.ui.components.word_cloud_component.st') as mock:
        yield mock

@pytest.fixture
def mock_domain_services():
    with patch('infrastructure.ui.components.word_cloud_component.build_corpus') as mock_build, \
         patch('infrastructure.ui.components.word_cloud_component.get_stopwords') as mock_stopwords, \
         patch('infrastructure.ui.components.word_cloud_component.WordCloud') as mock_wc_class:
        
        mock_build.return_value = "corpus text"
        mock_stopwords.return_value = set(["stop"])
        mock_wc_instance = MagicMock()
        mock_wc_class.return_value = mock_wc_instance
        
        yield {
            'build': mock_build,
            'stopwords': mock_stopwords,
            'wc_class': mock_wc_class,
            'wc_instance': mock_wc_instance
        }

def test_render_no_column(mock_streamlit):
    comp = WordCloudComponent()
    df = pd.DataFrame({'other': [1]})
    
    comp.render(df)
    
    mock_streamlit.info.assert_called_with("No se encontró la columna 'comentarios' para generar la nube.")

def test_render_empty_comments(mock_streamlit):
    comp = WordCloudComponent()
    df = pd.DataFrame({'comentarios': [None, None]})
    
    comp.render(df)
    
    mock_streamlit.info.assert_called_with("No hay comentarios disponibles para generar la nube de palabras.")

def test_render_empty_corpus(mock_streamlit, mock_domain_services):
    comp = WordCloudComponent()
    df = pd.DataFrame({'comentarios': ['a', 'b']})
    
    # Mock build_corpus return empty
    mock_domain_services['build'].return_value = ""
    
    comp.render(df)
    
    mock_streamlit.info.assert_called_with("Los comentarios disponibles no contienen suficiente texto para generar la nube.")

def test_render_success(mock_streamlit, mock_domain_services):
    comp = WordCloudComponent()
    df = pd.DataFrame({'comentarios': ['texto valido']})
    
    comp.render(df)
    
    # Check domain calls
    mock_domain_services['build'].assert_called()
    mock_domain_services['wc_class'].assert_called()
    
    # Check render calls
    mock_streamlit.image.assert_called()
    # Ensure correct object passed to image: wc_instance.generate().to_array()
    mock_domain_services['wc_instance'].generate.assert_called_with("corpus text")
    mock_domain_services['wc_instance'].generate.return_value.to_array.assert_called()
