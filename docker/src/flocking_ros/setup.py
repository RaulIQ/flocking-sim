from setuptools import find_packages, setup

setup(
    name='flocking_ros',
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/flocking_ros']),
        ('share/flocking_ros', ['package.xml']),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='RaulIQ',
    maintainer_email='raulalimbekov@gmail.com',
    description='The cloud on ROS 2: the board of every drone and the ground station',
    license='Proprietary',
    extras_require={'test': ['pytest', 'pyhamcrest']},
    entry_points={
        'console_scripts': [
            'board = flocking_ros.nodes.board:main',
            'ground = flocking_ros.nodes.ground:main',
            'flight = flocking_ros.nodes.flight:main',
            'home = flocking_ros.nodes.home:main',
            'origin = flocking_ros.nodes.origin:main',
        ],
    },
)
