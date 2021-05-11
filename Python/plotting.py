from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MaxNLocator
# import plotly.plotly as py
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

def plot_room_plotly(x_coord, y_coord, z_coord, point, distances, title, filename, color='brown'):
    x, y, z = [], [], []
    x_c, y_c, z_c = 0, 0, 0
    dx, dy, dz = 7.275, 4.0, 2.4
    for i in range(len(distances)):
        x.append((distances[i])[0])
        y.append((distances[i])[1])
        z.append((distances[i])[2])

    x_grid_lines = [0, dx, dx, 0, 0, 0, 0, 0, 0, dx, dx, dx, dx, dx, dx, 0]
    y_grid_lines = [0, 0, dy, dy, 0, 0, dy, dy, dy,dy, dy, dy, 0, 0, 0, 0]
    z_grid_lines = [0, 0, 0, 0, 0, dz, dz, 0, dz,dz, 0, dz, dz, 0, dz, dz]

    fig = go.Figure(data=[
        go.Scatter3d(mode='lines', x=x_grid_lines, y=y_grid_lines, z=z_grid_lines, opacity=1,
                     line=dict(width=2, color='#264653'), name='Room Setup'),
        go.Scatter3d(x=x_coord, y=y_coord, z=z_coord, mode='markers',
                     marker=dict(color="#264653", symbol='square', size=5), name="Speaker"),
        go.Scatter3d(x=[point[0]], y=[point[1]], z=[point[2]], mode='markers', name="Actual Position", marker=dict(color="#e9c46a")),
        go.Scatter3d(x=x, y=y, z=z,mode='markers', name="Estimated Position",marker=dict(color="#e76f51"))
        # go.Mesh3d(x = x_grid, y = y_grid, z = z_grid,i=i,j=j,k=k,opacity = 0.2, color = '#68829E',flatshading=True),

    ])
    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=2, y=-1.6, z=0.5)
    )
    fig.update_layout(scene_camera=camera, title=title, autosize=True)
    fig.update_scenes(zaxis_autorange ='reversed')
    fig.write_html(filename + ".html")
    fig.write_image(filename + ".svg")
    fig.show()

plt.rcParams['axes.unicode_minus'] = False

def plot_room_plotly_two_methods(x_coord, y_coord, z_coord, point, distances1, distances2, title, filename, color='brown'):
    x1, y1, z1 = [], [], []
    x2, y2, z2 = [], [], []
    x_c, y_c, z_c = 0, 0, 0
    dx, dy, dz = 7.275, 4.0, 2.4
    for i in range(len(distances1)):
        x1.append((distances1[i])[0])
        y1.append((distances1[i])[1])
        z1.append((distances1[i])[2])

    for j in range(len(distances2)):
        x2.append((distances2[j])[0])
        y2.append((distances2[j])[1])
        z2.append((distances2[j])[2])

    x_grid_lines = [0, dx, dx, 0, 0, 0, 0, 0, 0, dx, dx, dx, dx, dx, dx, 0]
    y_grid_lines = [0, 0, dy, dy, 0, 0, dy, dy, dy,dy, dy, dy, 0, 0, 0, 0]
    z_grid_lines = [0, 0, 0, 0, 0, dz, dz, 0, dz,dz, 0, dz, dz, 0, dz, dz]

    fig = go.Figure(data=[
        go.Scatter3d(mode='lines', x=x_grid_lines, y=y_grid_lines, z=z_grid_lines, opacity=1,
                     line=dict(width=2, color='#264653'), name='Room Setup'),
        go.Scatter3d(x=x_coord, y=y_coord, z=z_coord, mode='markers',
                     marker=dict(color="#264653", symbol='square', size=5), name="Speaker"),
        go.Scatter3d(x=[point[0]], y=[point[1]], z=[point[2]], mode='markers', name="Actual Position", marker=dict(color="#e9c46a",size=7)),
        go.Scatter3d(x=x1, y=y1, z=z1,mode='markers', name="Range Bancroft",marker=dict(color="#e76f51",size=5)),
        go.Scatter3d(x=x2, y=y2, z=z2, mode='markers', name="Chueng", marker=dict(color="#618B4A",size=5))
        # go.Mesh3d(x = x_grid, y = y_grid, z = z_grid,i=i,j=j,k=k,opacity = 0.2, color = '#68829E',flatshading=True),

    ])
    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=2, y=-1.6, z=0.5)
    )
    fig.update_layout(scene_camera=camera, title=title, autosize=True)
    fig.update_scenes(zaxis_autorange ='reversed')
    fig.write_html(filename + ".html")
    fig.write_image(filename + ".svg")
    fig.write_image(filename + ".pdf")
    fig.show()

plt.rcParams['axes.unicode_minus'] = False


def plot_references_plotly(x_coord, y_coord, z_coord, x_position, y_position, z_position, title, filename, color='brown'):
    x, y, z = [], [], []
    x_c, y_c, z_c = 0, 0, 0
    dx, dy, dz = 7.275, 4.0, 2.4

    x_grid_lines = [0, dx, dx, 0, 0, 0, 0, 0, 0, dx, dx, dx, dx, dx, dx, 0]
    y_grid_lines = [0, 0, dy, dy, 0, 0, dy, dy, dy,dy, dy, dy, 0, 0, 0, 0]
    z_grid_lines = [0, 0, 0, 0, 0, dz, dz, 0, dz,dz, 0, dz, dz, 0, dz, dz]

    fig = go.Figure(data=[
        go.Scatter3d(mode='lines', x=x_grid_lines, y=y_grid_lines, z=z_grid_lines, opacity=1,
                     line=dict(width=2, color='#264653'), name='Room Setup'),
        go.Scatter3d(x=x_coord, y=y_coord, z=z_coord, mode='markers',
                     marker=dict(color="#264653", symbol='square', size=5), name="Speaker"),
        go.Scatter3d(x=x_position, y=y_position, z=z_position, mode='markers', name="Actual Position", marker=dict(color="#e9c46a"))

    ])
    fig.update_layout(title=title, autosize=True)
    fig.update_scenes(zaxis_autorange ='reversed')
    fig.write_html(filename + ".html")
    fig.show()

plt.rcParams['axes.unicode_minus'] = False



def plot_error_color_plotly(x_coord, y_coord, z_coord, x_position, y_position, z_position, mean_error, title, filename, color='brown'):
    x, y, z = [], [], []
    x_c, y_c, z_c = 0, 0, 0
    dx, dy, dz = 7.275, 4.0, 2.4

    x_grid_lines = [0, dx, dx, 0, 0, 0, 0, 0, 0, dx, dx, dx, dx, dx, dx, 0]
    y_grid_lines = [0, 0, dy, dy, 0, 0, dy, dy, dy,dy, dy, dy, 0, 0, 0, 0]
    z_grid_lines = [0, 0, 0, 0, 0, dz, dz, 0, dz,dz, 0, dz, dz, 0, dz, dz]

    fig = go.Figure(data=[
        go.Scatter3d(mode='lines', x=x_grid_lines, y=y_grid_lines, z=z_grid_lines, opacity=1,
                     line=dict(width=2, color='#264653'), name='Room Setup'),
        go.Scatter3d(x=x_coord, y=y_coord, z=z_coord, mode='markers',
                     marker=dict(color="#264653", symbol='square', size=5), name="Speaker"),
        go.Scatter3d(x=x_position, y=y_position, z=z_position, mode='markers', name="Actual Position", marker=dict(color= mean_error, colorbar=dict(thickness=20, x = 0.9),cmin= 0, cmax = 19))
        # go.Scatter3d(x=x_position, y=y_position, z=z_position, mode='markers', name="Actual Position",
        #              marker=dict(color=mean_error, colorbar=dict(thickness=20, x=0.9)))

    ])
    fig.update_layout(title=title, autosize=True)
    fig.update_scenes(zaxis_autorange ='reversed')
    fig.write_html(filename + ".html")
    fig.show()

plt.rcParams['axes.unicode_minus'] = False

def plot_room(x_coord, y_coord, z_coord, point, distances, title, color='brown'):
    x, y, z = 0, 0, 0
    dx, dy, dz = 7.275, 4.0, 2.4
    fig = plt.figure()
    # plt.subplots_adjust(left=0., top=0.6, right=0.95, bottom=0.)
    ax = fig.add_subplot(111, projection='3d')
    # ax = Axes3D(fig)
    xx = [x, x, x + dx, x + dx, x]
    yy = [y, y + dy, y + dy, y, y]
    kwargs = {'alpha': 1, 'color': color}
    ax.plot3D(xx, yy, [z] * 5, **kwargs)
    ax.plot3D(xx, yy, [z + dz] * 5, **kwargs)
    ax.plot3D([x, x], [y, y], [z, z + dz], **kwargs)
    ax.plot3D([x, x], [y + dy, y + dy], [z, z + dz], **kwargs)
    ax.plot3D([x + dx, x + dx], [y + dy, y + dy], [z, z + dz], **kwargs)
    ax.plot3D([x + dx, x + dx], [y, y], [z, z + dz], **kwargs)

    ax.set_xlim(x, dx)
    ax.set_ylim(y, dy)
    ax.set_zlim(z, dz)
    ax.set_box_aspect((1, dy/dx, dz/dx))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.zaxis.set_major_locator(MaxNLocator(integer=True))
    ax.invert_zaxis()
    ax.scatter(x_coord[0], y_coord[0], z_coord[0], color = 'black', s=10)
    ax.scatter(x_coord[1], y_coord[1], z_coord[1], color = 'black',s=10)
    ax.scatter(x_coord[2], y_coord[2], z_coord[2], color = 'black',s=10)
    ax.scatter(x_coord[3], y_coord[3], z_coord[3], color = 'black',s=10)
    ax.scatter(point[0], point[1], point[2], color = 'g', s=10)
    for i in range(len(distances)):
        ax.scatter((distances[i])[0], (distances[i])[1], (distances[i])[2], color='red', s=10)

    plt.title(title)
    plt.show()

def plot_heatmap(distance_error, title, filename):


    speaker0 = go.Figure(data=go.Heatmap(
        z=np.flipud(np.transpose(np.array(distance_error[:,0]).reshape(10, 5))),
        x=['0.688', '1.277', '1.873', '2.478', '3.077', '3.676', '4.267', '4.877', '5.479', '6.081'],
        y=['0.797', '1.397', '1.996', '2.602', '3.197'],
        hoverongaps=False,
        zmin=0,
        zmax = 3.25
        ),
    )
    speaker0.update_layout(title=title + ' Speaker 0', autosize=True)
    speaker0.write_html(filename + "speaker0.html")
    speaker0.write_image(filename + "speaker0.svg")
    speaker0.show()

    speaker1 = go.Figure(data=go.Heatmap(
        z=np.flipud(np.transpose(np.array(distance_error[:, 1]).reshape(10, 5))),
        x=['0.688', '1.277', '1.873', '2.478', '3.077', '3.676', '4.267', '4.877', '5.479', '6.081'],
        y=['0.797', '1.397', '1.996', '2.602', '3.197'],
        hoverongaps=False,
        zmin = 0,
        zmax = 3.25))
    speaker1.update_layout(title=title + ' Speaker 1', autosize=True)
    speaker1.write_html(filename + "speaker1.html")
    speaker1.write_image(filename + "speaker1.svg")
    speaker1.show()

    speaker2 = go.Figure(data=go.Heatmap(
        z=np.flipud(np.transpose(np.array(distance_error[:, 2]).reshape(10, 5))),
        x=['0.688', '1.277', '1.873', '2.478', '3.077', '3.676', '4.267', '4.877', '5.479', '6.081'],
        y=['0.797', '1.397', '1.996', '2.602', '3.197'],
        hoverongaps=False,
        zmin = 0,
        zmax=3.25))

    speaker2.update_layout(title=title + ' Speaker 2', autosize=True)
    speaker2.write_html(filename + "speaker2.html")
    speaker2.write_image(filename + "speaker2.svg")
    speaker2.show()

    speaker3 = go.Figure(data=go.Heatmap(
        z=np.flipud(np.transpose(np.array(distance_error[:, 3]).reshape(10, 5))),
        x=['0.688', '1.277', '1.873', '2.478', '3.077', '3.676', '4.267', '4.877', '5.479', '6.081'],
        y=['0.797', '1.397', '1.996', '2.602', '3.197'],
        hoverongaps=False,
        zmin=0,
        zmax = 3.25))
    speaker3.update_layout(title=title + ' Speaker 3', autosize=True)
    speaker3.write_html(filename + "speaker3.html")
    speaker3.write_image(filename + "speaker3.svg")
    speaker3.show()

def plot_CDF(sortIntersection, sortRB, sortBeck, sortChueng, sortGN, title, filename):
    p = 1. * np.arange(len(sortIntersection)) / (len(sortIntersection) - 1)

    fig = go.Figure(data=[
        go.Scatter(x=sortIntersection, y=p, marker=dict(color='#264653'), name='Simple Intersection'),
        go.Scatter(x=sortRB, y=p, marker=dict(color='#2a9d8f'), name='Range Bancroft'),
        go.Scatter(x=sortBeck, y=p, marker=dict(color='#e9c46a'), name='Beck'),
        go.Scatter(x=sortChueng, y=p, marker=dict(color='#f4a261'), name='Chueng'),
        go.Scatter(x=sortGN, y=p, marker=dict(color='#e76f51'), name='Gauss Newton')
    ])
    fig.update_layout(title=title, autosize=True, xaxis_title = 'm', yaxis_title = 'CDF')
    fig.update_xaxes(range=[0, 20])
    fig.write_html(filename + ".html")
    fig.write_image(filename + ".svg")

    fig.show()



def plot_error_speaker(x_coord, y_coord, z_coord, x_position, y_position, z_position, distance_error, title, filename, color='brown'):
    x, y, z = [], [], []
    x_c, y_c, z_c = 0, 0, 0
    dx, dy, dz = 7.275, 4.0, 2.4

    x_grid_lines = [0, dx, dx, 0, 0, 0, 0, 0, 0, dx, dx, dx, dx, dx, dx, 0]
    y_grid_lines = [0, 0, dy, dy, 0, 0, dy, dy, dy,dy, dy, dy, 0, 0, 0, 0]
    z_grid_lines = [0, 0, 0, 0, 0, dz, dz, 0, dz,dz, 0, dz, dz, 0, dz, dz]

    speaker_0 = go.Figure(data=[
        go.Scatter3d(mode='lines', x=x_grid_lines, y=y_grid_lines, z=z_grid_lines, opacity=1,
                     line=dict(width=2, color='#264653'), name='Room Setup'),

        go.Scatter3d(x=[x_coord[0]], y=[y_coord[0]], z=[z_coord[0]], mode='markers',
                     marker=dict(color="#264653", symbol='square', size=5), name="Speaker"),
        go.Scatter3d(x=x_position, y=y_position, z=z_position, mode='markers', name="Actual Position", marker=dict(color= np.array(distance_error[:,0]), colorbar=dict(thickness=20, x = 0.9)))
    ])
    speaker_0.update_layout(title=title + " Speaker 0", autosize=True)
    speaker_0.update_scenes(zaxis_autorange ='reversed')
    speaker_0.write_html(filename +"speaker0" + ".html")
    speaker_0.write_image(filename + "speaker0" + ".svg")

    speaker_0.show()

    speaker_1 = go.Figure(data=[
        go.Scatter3d(mode='lines', x=x_grid_lines, y=y_grid_lines, z=z_grid_lines, opacity=1,
                     line=dict(width=2, color='#264653'), name='Room Setup'),

        go.Scatter3d(x=[x_coord[1]], y=[y_coord[1]], z=[z_coord[1]], mode='markers',
                     marker=dict(color="#264653", symbol='square', size=5), name="Speaker"),
        go.Scatter3d(x=x_position, y=y_position, z=z_position, mode='markers', name="Actual Position",
                     marker=dict(color=np.array(distance_error[:, 1]), colorbar=dict(thickness=20, x=0.9)))
    ])
    speaker_1.update_layout(title=title + " Speaker 1", autosize=True)
    speaker_1.update_scenes(zaxis_autorange='reversed')
    speaker_1.write_html(filename + "speaker1" + ".html")
    speaker_1.write_image(filename + "speaker1" + ".svg")
    speaker_1.show()

    speaker_2 = go.Figure(data=[
        go.Scatter3d(mode='lines', x=x_grid_lines, y=y_grid_lines, z=z_grid_lines, opacity=1,
                     line=dict(width=2, color='#264653'), name='Room Setup'),

        go.Scatter3d(x=[x_coord[2]], y=[y_coord[2]], z=[z_coord[2]], mode='markers',
                     marker=dict(color="#264653", symbol='square', size=5), name="Speaker"),
        go.Scatter3d(x=x_position, y=y_position, z=z_position, mode='markers', name="Actual Position",
                     marker=dict(color=np.array(distance_error[:, 2]), colorbar=dict(thickness=20, x=0.9)))
    ])
    speaker_2.update_layout(title=title + " Speaker 2", autosize=True)
    speaker_2.update_scenes(zaxis_autorange='reversed')
    speaker_2.write_html(filename + "speaker2" + ".html")
    speaker_2.write_image(filename + "speaker2" + ".svg")
    speaker_2.show()

    speaker_3 = go.Figure(data=[
        go.Scatter3d(mode='lines', x=x_grid_lines, y=y_grid_lines, z=z_grid_lines, opacity=1,
                     line=dict(width=2, color='#264653'), name='Room Setup'),

        go.Scatter3d(x=[x_coord[3]], y=[y_coord[3]], z=[z_coord[3]], mode='markers',
                     marker=dict(color="#264653", symbol='square', size=5), name="Speaker"),
        go.Scatter3d(x=x_position, y=y_position, z=z_position, mode='markers', name="Actual Position",
                     marker=dict(color=np.array(distance_error[:, 3]), colorbar=dict(thickness=20, x=0.9)))
    ])
    speaker_3.update_layout(title=title + " Speaker 3", autosize=True)
    speaker_3.update_scenes(zaxis_autorange='reversed')
    speaker_3.write_html(filename + "speaker3" + ".html")
    speaker_3.write_image(filename + "speaker3" + ".svg")
    speaker_3.show()


plt.rcParams['axes.unicode_minus'] = False

 # i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    # j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    # k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    #
    # x_grid = [x_c, x_c, x_c + dx, x_c + dx, x_c, x_c, x_c + dx , x_c +dx]
    # y_grid = [y_c, y_c + dy, y_c + dy, y_c, y_c, y_c + dy, y_c + dy, y_c]
    # z_grid = [z_c, z_c, z_c, z_c, z_c + dz, z_c + dz, z_c + dz, z_c + dz]