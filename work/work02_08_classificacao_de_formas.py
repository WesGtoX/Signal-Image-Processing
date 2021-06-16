# -*- coding: utf-8 -*-
"""work02_08_classificacao_de_formas.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11HWnKJH1LnvnlGvCvQ7hdaZ9mI5JvlsX

# **Processamento de Imagens e Imagens**
Engenharia da Computação - 2021.01

**Wesley de Oliveira Mendes, 828.507**

## Tarefa 08 - Classificação de Formas
- Objetivo
    - Desenvolver um sistema de visão computacional para classificação de formas.

### Download das imagens

### Imports
"""

import cv2 as cv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

"""### Code

#### Exercício
"""

path = '/content/drive/MyDrive/Colab Notebooks/College/Signal-Image-Processing/data/frutas_dataset'

classification = (
    ('001', '030', 'Maça'),
    ('031', '060', 'Abacaxi'),
    ('061', '090', 'Banana'),
    ('091', '120', 'Pêssego'),
    ('121', '150', 'Pitanga'),
    ('151', '180', 'Laranja'),
    ('181', '210', 'Morango'),
    ('211', '240', 'Pera'),
    ('241', '270', 'Limão'),
    ('271', '300', 'Uva')
)

# dicionario para salvar dados das imagens
dataset = {
    'Diameter': [], 
    'Perimeter': [], 
    'Area': [], 
    'Compactness': [], 
    'Eccentricity': [],
    'Rectangularity': [],
    'Solidity': [], 
    'Classes': [],
}

# loop para extrar dados de indices
for start, end, classes in classification:
    # loop para extrar dados das imagens
    for i in range(int(start), int(end) + 1):
        image = cv.imread(f'{path}/{i:03d}.bmp')
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        
        _, image = cv.threshold(image, 127, 255, cv.THRESH_BINARY_INV)
        contour, order = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        # extrair diametro
        diameter = np.sqrt(4 * cv.contourArea(contour[0]) / np.pi)
        dataset['Diameter'].append(float(diameter))

        # extrair perimetro
        perimeter = cv.countNonZero(cv.Canny(image, 50, 100))
        dataset['Perimeter'].append(float(perimeter))

        # extrair area
        area = cv.countNonZero(image)
        dataset['Area'].append(float(area))
        
        # extrair compacidade
        compactness = np.square(perimeter / area)
        dataset['Compactness'].append(float(compactness))

        # extrair excentricidade
        eccentricity = 0
        
        if len(contour[0]) > 5:
            (x, y), (minor_axis, major_axis), angle = cv.fitEllipse(contour[0])
            eccentricity = major_axis / minor_axis
        
        dataset['Eccentricity'].append(float(eccentricity))

        # extrair retangularidade
        compactness = np.square(perimeter / area)
        dataset['Rectangularity'].append(float(compactness))

        # extrair solidez
        area_obj = cv.contourArea(contour[0])
        area_fechoconvexo = cv.contourArea(cv.convexHull(contour[0]))
        solidity = area_obj / area
        dataset['Solidity'].append(float(solidity))
        
        # especificar classe da imagem
        dataset['Classes'].append(classes)

# criar datafram pandas a partir do dicionario gerado
df = pd.DataFrame(dataset)
df.head()

# extrair label de classificacao
labels = df['Classes'].astype('category').cat.categories.tolist()
labels_to_replace = {'Classes' : {k: v for k,v in zip(labels, list(range(1, len(labels) + 1)))}}
print(labels_to_replace)

# substituir label texto de classificacao para numerico
df.replace(labels_to_replace, inplace=True)
dataframe = df.copy()
dataframe.head()

# remover colunas desnecessarias
df.drop(['Diameter', 'Solidity'], axis=1, inplace=True)
df.head()

# separar as caracteristicas e os rotulos
X = df.iloc[:, :3]  # caracteristicas 
y = df.iloc[:, -1]  # rotulos

# PROCESSAMENTO
# dividir o conjunto de dados em treinamento e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=25)

# normalizacao dos dados
normalize = StandardScaler()
normalize.fit(X_train)

X_train = normalize.transform(X_train)
X_test = normalize.transform(X_test)

# classificador
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train, y_train)
Y = knn.predict(X_test)

# resultado
acc = accuracy_score(y_test, Y)
print(f'Accuracy {acc:.2f}\n')

# Matriz confusao
print(pd.crosstab(y_test, Y, rownames=['True'], colnames=['Predicao'], margins=True))