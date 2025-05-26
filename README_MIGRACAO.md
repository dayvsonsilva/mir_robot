# Guia de Migração para ROS 2 Jazzy e Gazebo Harmonic

Este documento descreve as alterações realizadas no repositório mir_robot para garantir compatibilidade com ROS 2 Jazzy e Gazebo Harmonic.

## Principais Alterações

### 1. Substituição de Dependências

- **Removidas**:
  - `gazebo_ros`
  - `gazebo_ros_pkgs`
  - `gazebo`

- **Adicionadas**:
  - `ros_gz_sim`
  - `ros_gz_bridge`
  - `ros_gz_image`

### 2. Atualização de Plugins

Todos os plugins do Gazebo Classic foram substituídos por equivalentes do Gazebo Harmonic:

- `libgazebo_ros_ray_sensor.so` → `libgz_ros_ray_sensor.so`
- `libgazebo_ros_imu_sensor.so` → `libgz_ros_imu_sensor.so`
- `libgazebo_ros_joint_state_publisher.so` → `libgz_ros_joint_state_publisher.so`
- `libgazebo_ros_diff_drive.so` → `libgz_ros_diff_drive.so`
- `libgazebo_ros_p3d.so` → `libgz_ros_p3d.so`
- `libgazebo_ros2_control.so` → `libgz_ros2_control.so`

### 3. Atualização de Launch Files

- Substituição de chamadas ao `gazebo_ros/launch/gazebo.launch.py` por `ros_gz_sim/launch/gz_sim.launch.py`
- Atualização dos argumentos de linha de comando para o formato do Gazebo Harmonic
- Substituição do nó `spawn_model` do `gazebo_ros` por `create` do `ros_gz_sim`

### 4. Atualização de Variáveis de Ambiente

- Substituição de `gazebo_model_path` por `gz_sim_path` nas tags de exportação do package.xml

## Instruções de Uso

1. Instale o ROS 2 Jazzy e os pacotes necessários:
   ```bash
   sudo apt install ros-jazzy-ros-gz-sim ros-jazzy-ros-gz-bridge ros-jazzy-ros-gz-image
   ```

2. Clone o repositório atualizado em seu workspace:
   ```bash
   mkdir -p ~/mir_ws/src
   cd ~/mir_ws/src
   # Extraia o conteúdo do arquivo zip aqui
   ```

3. Compile o workspace:
   ```bash
   cd ~/mir_ws
   colcon build
   ```

4. Execute a simulação:
   ```bash
   source install/setup.bash
   ros2 launch mir_gazebo mir_gazebo_launch.py
   ```

## Observações

- Este repositório foi atualizado seguindo as melhores práticas do guia oficial de migração do Gazebo Classic para o Gazebo Harmonic.
- Todos os arquivos foram revisados e atualizados para garantir compatibilidade total com ROS 2 Jazzy.
- Se encontrar algum problema durante a compilação ou execução, verifique se todos os pacotes necessários estão instalados.
