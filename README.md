# [💟 Anime Daisuki! API](https://documenter.getpostman.com/view/17890889/UV5ZAbTe)

### API de animes com cadastro de usuários. O usuário autenticado pode avaliar e favoritar animes, comentar episódios e verificar o histórico de episódios assistidos

#### Projeto concluído ✔️

[Sobre](#sobre) • [Tecnologias](#tecnologias) • [Instalação](#instalação) • [Demonstração](#demonstração) • [Autores](#autores) • [Licença](#licença)

## Sobre

Projeto desenvolvido no terceiro trimestre da Kenzie Academy Brasil com o objetivo de criar uma API, aplicando os conceitos de CRUD, SQL, migrations, autenticação (JSON Web Tokens) e segurança (geração de hash para senha). Anime Daisuki! API é uma aplicação de cadastro de usuários, animes, episódios e comentários. Você pode utilizar o deploy no [Heroku](https://animedaisuki.herokuapp.com/api) e fazer requisições de qualquer client seguindo os endpoints /users, /animes e /episodes na [documentação](https://documenter.getpostman.com/view/17890889/UV5ZAbTe).
Caso queira rodar a aplicação na sua própria máquina, siga as instruções na seção [Instalação](#instalação).


## Tecnologias

As seguintes ferramentas foram utilizadas na construção do projeto:

- [Python](https://docs.python.org/3/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [PostgreSQL](https://www.postgresql.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [JWT](https://jwt.io/)

## Instalação

Renomeie o arquivo .env.example para .env e preencha com as informações do banco que deseja utilizar. Ative o ambiente virtual seguindo os comandos:

```
python -m venv venv
```

```
source venv/bin/activate
```

Agora, dentro do ambiente virtual, insira o comando para instalar as dependências:

```
pip install -r requirements.txt
```

Para que as tabelas sejam inseridas no seu banco de dados, rode o comando:

```
flask db upgrade
```

Insira dados nas tabelas com os seguintes comandos (nessa ordem):

```
flask cli_genres create
flask cli_animes create
flask cli_episodes create
```

Inicie o flask:

```
flask run
```

Pronto! Agora você já pode fazer requisições seguindo os endpoints na seção [Demonstração](#demonstração), substituindo a url do heroku pelo localhost. Mas caso queira cadastrar um usuário com permissão de admin, insira o seguinte comando substituindo por seu e-mail, usuário e senha:

```
flask cli_admin create teste@gmail.com teste 1234
```

É possível também promover um usuário já cadastrado com o comando:

```
flask cli_admin upgrade --email=teste@gmail.com
```

ou

```
flask cli_admin upgrade --username=teste
```

E para remover o cargo de admin, tornando-o um usuário comum, rode o comando:

```
flask cli_admin downgrade teste@gmail.com
```

ou utilize o parâmetro --permission para torná-lo um moderador

```
flask cli_admin downgrade teste@gmail.com --permission=mod
```

## Demonstração 

Todos os endpoints da aplicação estão descritos na [documentação](https://documenter.getpostman.com/view/17890889/UV5ZAbTe). A rota de criação de users no [Heroku](https://animedaisuki.herokuapp.com/api) permite somente a criação de usuários comuns, então para criar um admin ou mod siga os últimos comandos da seção acima e faça as requisições utilizando um client como o Postman e substituindo a url com o localhost:

![Postman](https://i.imgur.com/BW8KNef.png)

## Autores

Feito com ❤️ por:
<div style="display: flex; gap: 8px;">
<div style="text-align: center;">
<a href="https://www.linkedin.com/in/laianesuzart/">
 <img style="border-radius: 50%;" src="https://media-exp1.licdn.com/dms/image/C5603AQHAdjbAfjBHUA/profile-displayphoto-shrink_800_800/0/1629663203064?e=1640217600&v=beta&t=bQfDZ5_uwIT3W-vXShtzMRs5pz7ugQrD78TFtGcQPhU" width="80px;" alt=""/>
 <br />
 <sub><b>Laiane Suzart</b></sub></a> 
 <a href="https://github.com/laianesuzart">
 <img width="20px" style="margin-bottom: -8px" src="https://cdn.iconscout.com/icon/free/png-256/github-1521500-1288242.png"/>
 </a>
 </div>
<div style="text-align: center;">
 <a href="https://www.linkedin.com/in/paulothorsilva/">
 <img style="border-radius: 50%;" src="https://media-exp1.licdn.com/dms/image/C4E03AQG2NgjEZrpKlA/profile-displayphoto-shrink_800_800/0/1629380759714?e=1640217600&v=beta&t=Pr1pX3N3jXccoFowwc24FGuiWx5FmQjpdknD3RjqNLM" width="80px;" alt=""/>
 <br />
 <sub><b>Paulo Thor</b></sub></a> 
 <a href="https://github.com/PauloThor">
 <img width="20px" style="margin-bottom: -8px" src="https://cdn.iconscout.com/icon/free/png-256/github-1521500-1288242.png"/>
 </a>
 </div>
 <div style="text-align: center;">
 <a href="https://www.linkedin.com/in/thainaferreira/">
 <img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/74427328?v=4" width="80px;" alt=""/>
 <br />
 <sub><b>Thainá Ferreira</b></sub></a> 
 <a href="https://github.com/thainaferreira">
 <img width="20px" style="margin-bottom: -8px" src="https://cdn.iconscout.com/icon/free/png-256/github-1521500-1288242.png"/>
 </a>
 </div>
 <div style="text-align: center;">
 <a href="https://www.linkedin.com/in/matheus-paiva-vieira/">
 <img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/82341020?v=4" width="80px;" alt=""/>
 <br />
 <sub><b>Matheus Paiva</b></sub></a> 
 <a href="https://github.com/matheuspaivah2">
 <img width="20px" style="margin-bottom: -8px" src="https://cdn.iconscout.com/icon/free/png-256/github-1521500-1288242.png"/>
 </a>
 </div>
 <div style="text-align: center;">
 <a href="https://www.linkedin.com/in/emanuela-biondo-quizini-245ab0195/">
 <img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/87705090?v=4" width="80px;" alt=""/>
 <br />
 <sub><b>Emanuela Quizini</b></sub></a> 
 <a href="https://github.com/emanuelakenzie">
 <img width="20px" style="margin-bottom: -8px" src="https://cdn.iconscout.com/icon/free/png-256/github-1521500-1288242.png"/>
 </a>
 </div>
</div>

## Licença

Este projeto está sob a licença [MIT](https://choosealicense.com/licenses/mit/).
