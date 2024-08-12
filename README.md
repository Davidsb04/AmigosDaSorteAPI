# AmigosDaSorteAPI

AmigosDaSorteAPI é uma API desenvolvida em Flask para a criação e gestão de grupos de apostas entre amigos. A API interage com o Firebase Firestore como banco de dados e consome dados da API-Football para obter resultados de jogos.

## Visão Geral

Esta API permite a criação e gestão de grupos de apostas entre amigos, incluindo operações relacionadas a usuários, grupos, apostas e verificação de resultados de partidas.

## Autenticação

A API utiliza sessões para autenticação. Cada rota que requer autenticação do usuário verifica a presença de um `user_id` na sessão (Exceto a rota `/create_user`).

## Rotas

### 1. Account

#### Registrar Usuário
- **`POST /create_user`**
- **Descrição:** Registra um novo usuário na plataforma.
- **Parâmetros no Body (JSON):**
  - `email`: (string) - O e-mail do usuário.
  - `username`: (string) - O nome de usuário.
  - `password`: (string) - A senha do usuário.
- **Resposta:**
  - `201 Created`: Usuário registrado com sucesso.
  - `400 Bad Request`: Todos os campos são obrigatórios.
  - `409 Conflict`: E-mail ou nome de usuário já utilizado.
  
##### Exemplo de Requisição:
```json
{
  "email": "usuario@exemplo.com",
  "username": "usuario123",
  "password": "minhasenha"
}
```

#### Retornar Usuários
- **`GET /users`**
- **Descrição:** Retornar os usuários cadastrados na plataforma.
- **Resposta:**
  - `200 OK`: Retorna os usuários encontrados.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.
  - `404 Not Found`: Nenhum usuário cadastrado foi encontrado.

 
#### Atualizar Dados do Usuário
- **`PUT /update_user`**
- **Descrição:** Atualiza os dados do usuário conectado.
- **Parâmetros no Body (JSON):**
  - `email`: (string) - O e-mail do usuário.
  - `username`: (string) - O nome de usuário.
  - `password`: (string) - A senha do usuário.
- **Resposta:**
  - `200 OK`: Dados do usuário atualizado.
  - `400 Bad Request`: Todos os campos são obrigatórios.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.
  - `404 Not Found`: Usuário não encotrado.
  - `409 Conflict`: E-mail ou nome de usuário já utilizado.

##### Exemplo de Requisição:
```json
{
  "email": "usuario@exemplo.com",
  "username": "usuarioatualizado",
  "password": "minhasenha"
}
```

#### Excluir Usuário
- **`DELETE /delete_user`**
- **Descrição:** Excluí o usuário conectado.
- **Resposta:**
  - `204 No Content`: Usuário deletado.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.
  - `404 Not Found`: Usuário não encontrado.

 ### 2. Login

 #### Conectar Usuário
- **`POST /login`**
- **Descrição:** Conecta um usuário à plataforma criando a sessão.
- **Parâmetros no Body (JSON):**
  - `email`: (string) - O e-mail do usuário.
  - `password`: (string) - A senha do usuário.
- **Resposta:**
  - `201 Created`: Usuário conectado com sucesso.
  - `400 Bad Request`: Insira todos os campos.
  - `401 Unauthorized`: Senha inválida.
  - `404 Not Found`: Usuário não encontrado.
  - `500 Internal Server Error`: Não foi possível efetuar o login.
  
##### Exemplo de Requisição:
```json
{
  "email": "usuario@exemplo.com",
  "password": "minhasenha"
}
```

 #### Desconectar Usuário
- **`POST /logout`**
- **Descrição:** Encerra a sessão do usuário que estava conectado.
- **Resposta:**
  - `204 No Content`: Usuário desconectado com sucesso.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.

 #### Retornar Usuário Logado
- **`GET /current_user`**
- **Descrição:** Retorna os dados do usuário que está conectado.
- **Resposta:**
  - `200 Ok`: Retorna e-mail e nome de usuário.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.
  - `404 Not Found`: Usuário não encontrado.

### 3. Group

#### Criar um Grupo
- **`POST /create_group`**
- **Descrição:** Registra um novo grupo na plataforma.
- **Parâmetros no Body (JSON):**
  - `group_name`: (string) - Nome do grupo.
  - `group_password`: (string) - Senha do grupo.
- **Resposta:**
  - `201 Created`: Grupo criado com sucesso.
  - `400 Bad Request`: Insira todos os campos.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.
  - `500 Internal Server Error`: Não foi possível criar o grupo.
  
##### Exemplo de Requisição:
```json
{
  "group_name": "nomedogrupo",
  "group_password": "senhadogrupo"
}
```

#### Entrar em um Grupo
- **`POST /join_group/<group_id>`**
- **Descrição:** Usuário ingressa em um grupo já existente.
- **Parâmetros no Body (JSON):**
  - `group_name`: (string) - Nome do grupo.
  - `group_password`: (string) - Senha do grupo.
- **Resposta:**
  - `200 Ok`: Usuário inserido no grupo.
  - `401 Unauthorized`: Senha inválida. ou Nenhum usuário conectado foi encontrado.
  - `404 Not Found`: Esse grupo não foi encontrado.
  - `409 Conflict`: Usuário já faz parte do grupo.
  - `500 Internal Server Error`: Não foi possível ingressar no grupo.
  
##### Exemplo de Requisição:
```json
{
  "group_name": "nomedogrupo",
  "group_password": "senhadogrupo"
}
```
#### Retornar Grupo pelo Nome
- **`GET /group/<group_name>`**
- **Descrição:** Retorna os grupos com o nome passado pela URL.
- **Resposta:**
  - `200 Ok`: Retorna grupos encontrados.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.
  - `404 Not Found`: Grupo não encontrado.
    
#### Retornar Apostas do Usuário
- **`GET /user_bets/<group_name>`**
- **Descrição:** Retorna as últimas apostas feitas pelo usuário conectado no grupo em questão.
- **Resposta:**
  - `200 Ok`: Apostas realizadas pelo usuário.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.
  - `404 Not Found`: Nenhuma aposta foi encontrada.

#### Atualizar Dados do Grupo
- **`PUT /update_group/<group_id>`**
- **Descrição:** Atualiza os dados do grupo passado na URL.
- **Parâmetros no Body (JSON):**
  - `group_name`: (string) - Nome do grupo.
  - `group_password`: (string) - A senha do grupo.
- **Resposta:**
  - `200 OK`: Dados do grupo atualizado.
  - `400 Bad Request`: Todos os campos são obrigatórios.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.
  - `403 Forbidden`: Apenas o dono do grupo pode fazer alterações.
  - `404 Not Found`: Grupo não encontrado.

##### Exemplo de Requisição:
```json
{
  "group_name": "nomedogrupo",
  "group_password": "senhadogrupo"
}
```

#### Sair do Grupo
- **`PUT /leave_group/<group_id>`**
- **Descrição:** O usuário conectado é removido do grupo passado na URL.
- **Resposta:**
  - `204 No Content`: Dados do grupo atualizado.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.

#### Excluir Grupo
- **`DELETE /delete_group/<group_id>`**
- **Descrição:** Excluí o grupo passado na URL.
- **Resposta:**
  - `204 No Content`: Grupo deletado com sucesso.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.
  - `404 Not Found`: Nenhum grupo foi encontrado.
 
### 4. Bet

#### Registrar Aposta
- **`POST /place_bet/<group_id>/<match_id>`**
- **Descrição:** Registra a aposta feita pelo usuário no grupo passado pela URL.
- **Parâmetros no Body (JSON):**
  - `home_score`: (string) - Gols do time da casa.
  - `away_score`: (string) - Gols do time de fora.
- **Resposta:**
  - `201 Created`: Aposta registrada com sucesso.
  - `400 Bad Request`: Placares da partida não inseridos.
  - `403 Forbidden`: Usuário não autorizado ou grupo não encontrado.
  - `401 Conflict`: Nenhum usuário conectado foi encontrado.
  - 
##### Exemplo de Requisição:
```json
{
  "home_score": "1",
  "away_score": "2"
}
```

#### Validar Aposta
- **`POST /check_bet/<group_id>/<match_id>`**
- **Descrição:** Verifica se a aposta feita pelo usuário na partida passada na URL foi acertiva ou não.
- **Resposta:**
  - `200 Ok`: {result} a aposta.
  - `401 Conflict`: Nenhum usuário conectado foi encontrado.
  - `404 Not Found`: Aposta não encontrada.
  - `505 Internal Server Error`: Não foi possível obter o resultado da partida.

#### Retornar a Próxima Rodada
- **`GET /next_round`**
- **Descrição:** Retorna os próximos 10 jogos do Brasileirão Serie A (Corresponde a uma rodada).
- **Resposta:**
  - `200 Ok`: Retorna os jogos.
  - `401 Unauthorized`: Nenhum usuário conectado foi encontrado.
  - `505 Internal Server Error`: Não foi possível retornar os confrontos.
