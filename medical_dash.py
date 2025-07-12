import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc  

# Загрузка и подготовка данных
file_path = 'dataset.xlsx'
df = pd.read_excel(file_path)

# Преобразование дат в правильный формат
df['ExamDate'] = pd.to_datetime(df['ExamDate'])

# Инициализация приложения с Bootstrap темой
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1('Медицинский Dashboard', className='text-center my-4'),

    # Checklist для выбора группы
    dbc.Row([
        dbc.Col([
            html.Label('Выбор группы:'),
            dcc.Checklist(
                id='group-checklist',
                options=[{'label': f'Группа {g}', 'value': g} for g in sorted(df['Group'].unique())],
                value=sorted(df['Group'].unique()),
                inline=True
            )
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='scatter-plot'), width=6),
        dbc.Col(dcc.Graph(id='pie-chart'), width=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart'), width=6),
        dbc.Col(dcc.Graph(id='histogram'), width=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='box-plot'), width=6),
        dbc.Col(dcc.Graph(id='heatmap'), width=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart'), width=6),
        dbc.Col(dcc.Graph(id='animated-scatter'), width=6)
    ])
], fluid=True)

# Callback для обновления графиков
@app.callback(
    Output('scatter-plot', 'figure'),
    Output('pie-chart', 'figure'),
    Output('bar-chart', 'figure'),
    Output('histogram', 'figure'),
    Output('box-plot', 'figure'),
    Output('heatmap', 'figure'),
    Output('line-chart', 'figure'),
    Output('animated-scatter', 'figure'),
    Input('group-checklist', 'value')
)
def update_graphs(selected_groups):
    # Создаем пустую фигуру для случаев отсутствия данных
    empty_fig = px.scatter(title="Нет данных для отображения")
    
    if not selected_groups:
        return [empty_fig] * 8
    
    filtered = df[df['Group'].isin(selected_groups)]
    if filtered.empty:
        return [empty_fig] * 8

    # Scatter Plot - Гемоглобин vs Ферритин
    scatter_fig = px.scatter(
        filtered,
        x='Ferritin', 
        y='Hemoglobin',
        color='Group',
        hover_name='ID',
        title='Гемоглобин vs Ферритин'
    )

    # Pie Chart - Распределение по группам
    pie_fig = px.pie(
        filtered,
        names='Group',
        title='Распределение по группам'
    )

    # Bar Chart - Средний гемоглобин по группам
    bar_data = filtered.groupby('Group', observed=True, as_index=False)['Hemoglobin'].mean()
    bar_fig = px.bar(
        bar_data,
        x='Group', 
        y='Hemoglobin',
        title='Средний гемоглобин по группам'
    )

    # Histogram - Распределение общего белка
    hist_fig = px.histogram(
        filtered,
        x='Protein', 
        nbins=20,
        color='Group',
        title='Распределение общего белка'
    )

    # Box Plot - Распределение ферритина по полу
    box_fig = px.box(
        filtered,
        x='Sex', 
        y='Ferritin',
        color='Sex',
        title='Распределение ферритина по полу'
    )

    # Heatmap - Самочувствие по гемоглобину и белку
    try:
        heatmap_df = filtered.copy()

        heatmap_df['Hb_bin'] = pd.cut(heatmap_df['Hemoglobin'], bins=6).astype(str)
        heatmap_df['Protein_bin'] = pd.cut(heatmap_df['Protein'], bins=6).astype(str)

        heat_data = heatmap_df.groupby(['Hb_bin', 'Protein_bin'], observed=True)['SelfRatedHealth'].mean().reset_index()
        heatmap_pivot = heat_data.pivot(index='Hb_bin', columns='Protein_bin', values='SelfRatedHealth')
        
        heatmap_fig = px.imshow(
            heatmap_pivot,
            labels=dict(x='Общий белок', y='Гемоглобин', color='Самочувствие'),
            title='Самочувствие по белку и гемоглобину'
        )
    except Exception as e:
        print(f"Ошибка при создании heatmap: {e}")
        heatmap_fig = empty_fig

    # Line Chart - Пульс по дате обследования
    line_fig = px.line(
        filtered.sort_values('ExamDate'),
        x='ExamDate', 
        y='HeartRate',
        color='Group',
        title='ЧСС (пульс) по дате обследования'
    )

    # Animated Scatter - Гемоглобин против ферритина с возрастом
    try:
        animated_fig = px.scatter(
            filtered,
            x='Ferritin', 
            y='Hemoglobin',
            animation_frame='Age',
            size='HeartRate', 
            color='Group',
            hover_name='ID',
            title='Анимация: гемоглобин vs ферритин по возрасту',
            animation_group='ID',
            range_x=[filtered['Ferritin'].min(), filtered['Ferritin'].max()],
            range_y=[filtered['Hemoglobin'].min(), filtered['Hemoglobin'].max()]
        )
    except Exception as e:
        print(f"Ошибка при создании анимированного графика: {e}")
        animated_fig = empty_fig

    return (
        scatter_fig, 
        pie_fig, 
        bar_fig, 
        hist_fig, 
        box_fig, 
        heatmap_fig, 
        line_fig, 
        animated_fig
    )

if __name__ == '__main__':
    app.run(debug=True)
    
