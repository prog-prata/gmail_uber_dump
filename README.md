<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contribuições)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

<p style="text-align:center;">
  <h1>Dump Uber Gmail</h1>
  <!-- Incluindo alguns badges: START-->
  <a href="https://github.com/prog-prata/gmail_uber_dump/blob/master/LICENSE" target="blank">
    <img src="https://img.shields.io/github/license/prog-prata/gmail_uber_dump?style=flat-square" alt="gmail_uber_dump licence" />
  </a>
  <!-- Incluindo alguns badges: END-->
</p>

Este projeto é um aplicativo que acessa sua conta do **Gmail** e faz o _"dump"_ dos e-mail enviados pela **UBER** contedo os _recibos das viagens_ feitas usando o app da empresa.  
O programa irá gerar um arquivo chamado `data/emails.json` no formato JSON que poderá ser utilizado para analisar as informações de suas viagens.  
Este arquivo vai conter as seguintes informações:

- O valor total pago, a distância percorrida, a data da viagem e quando for possível os endereços de partida e destino.

## Instalação

1. Clonar o repositório:

```
git clone https://github.com/prog-prata/gmail_uber_dump.git
```

2. Criar uma senha de aplicativo para acess o GMAIL, para isso seguir as instruções deste [link](https://support.google.com/accounts/answer/185833?hl=pt-BR). Note que será necessário ativar a verificação em duas etapas na sua conta do Google.
3. Renomear o arquivo `config/credentials_sample.json` para `config/credentials.json` e inserir no campo **user** seu endereço de e-mail e no campo **password** a senha de aplicativo que foi criada no passo anterior.
4. Para completar a instalação, vá para a pasta onde foi clonado o repositório e execute o pip para instalar as dependências:

```
cd gmail_uber_dump
pip install -r requirements.txt
```

## Uso

Para usar o aplicativo execute o comando abaixo informando os parâmetros conforme descrito a seguir:

```
python dump_uber.py [-h] [--delete] --since SINCE
```

**Parâmetros:**

- `-h` : exibe a ajuda do programa
- `--delete` : é um flag que quando for incluído vai **deletar** as mensagens dos recibo da UBER de sua **Caixa de Entrada** após fazer o respetivo dump.
- `--since SINCE` : parâmetro obrigatório usado para informar ao programa a partir de que data devem ser processadas as mensagens. Deve ser informado entre aspas e conter a data no formato "dd/mm/aaaa hh:mm", **atenção** o horário tem de ser informado.  
  _Exemplos:_

```
python dump_uber.py --since "01/11/2024 00:00"
```

Vai considerar as mensagens recebidas a partir da meia-noite do dia primeiro de novembro de 2024 e vai mantê-las na caixa de entrada.

```
python dump_uber.py --delete --since "15/08/2024 17:00"
```

Processa as mensagens recebidas a partir das 17 horas do dia quinze de agosto de 2024 e vai remover as mensagens da caixa de entrada.

## Observações

- As mensagens serão gravadas na pasta `data` em um arquivo com o nome `emails.json`.
- Este arquivo é **cumulativo**, ou seja, execuções sucessivas vão acrescentar mais mensagens sem apagar as anteriores. Porém o arquivo **não será ordenado**, pois a ideia é usar um outro aplicativo (Pandas por exemplo) para tratar o arquivo e extrair informações.
- Para obter endereços de **partida** e **destino** o programa tenta encontrar o CEP. Assim caso no cadastro do endereço não exista o CEP o programa não encontrará o endereço e o campo _address_ será vazio.
- Pelo mesmo motivo, caso haja na mensagem algum texto / parágrafo que siga o mesmo padrão do CEP, poderá ser gerado um campo _address_ com um endereço inexistente.
- Em alguns casos ocorreu um erro de acesso ao gmail devido a problemas no protocolo IMAP que não são do programa. A mensgem de erro é algo como `imaplib.IMAP4.error: LOGIN command error`. Se ocorrer um error semelhante tente reexceutar o programa algumas vezes.
- A execução pode ser demorada, então é recomendável definir uma data (parâmtro SINCE) mais recente e depois ir ajustando para datas mais antigas.

## Configurações e Pastas

- As credencias do gmail devem ser informadas no arquivo `credentials.json` que está localizado na pasta `config`.
- O arquivo `uber_list.json` que está na pasta `mail_list` contém os endereços dos remetentes dos recibo da UBER.

## Contribuições

Este projeto segue a especificação [all-contributors](https://github.com/all-contributors/all-contributors). Contribuições de qualquer tipo, especialmente ajuda com o código do projeto, serão bem-vindas!
