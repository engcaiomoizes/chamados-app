# 🚀 TI Command Center

Um painel operacional leve e moderno para organização e triagem de chamados de TI, desenvolvido em **Python (Flask)**, **SQLite** e **Tailwind CSS**, totalmente preparado para execução em ambientes containerizados com **Docker**.

---

## 📋 Pré-requisitos

Certifique-se de ter as seguintes ferramentas instaladas em sua máquina:
* **Docker** (versão 20.10 ou superior)
* **Docker Compose** (versão 2.0 ou superior)

---

## ⚙️ 1. Configuração do Ambiente (`.env`)

Para garantir a segurança de chaves sensíveis e dados da sessão, a aplicação utiliza variáveis de ambiente.

1. Na raiz do projeto, crie um arquivo chamado **`.env`**.
2. Insira a chave secreta com um valor seguro:

```env
SECRET_KEY=sua_chave_secreta_super_segura_aqui
```

> **Aviso:** Nunca versione o arquivo `.env` no controle de versão (ele já vem bloqueado no `.gitignore`).

---

## 🐳 2. Como Rodar a Aplicação via Docker

Com o Docker instalado e em execução no seu sistema, siga os passos abaixo:

1. Abra o terminal na pasta raiz do projeto.
2. Execute o comando para construir a imagem e subir o container em segundo plano:
   ```bash
   docker compose up -d --build
   ```
3. O container estará rodando ativamente e vinculado à porta `5000` da sua máquina.

---

## 🌐 3. Como Utilizar o Sistema

1. Abra o navegador web de sua preferência e acesse:
   ```text
   http://localhost:5000
   ```
2. **Autenticação (Login):**
   * No primeiro acesso, utilize as credenciais padrão de administrador:
     * **Usuário:** `admin`
     * **Senha:** `admin123`
3. **Funcionalidades do Painel:**
   * **Novo Chamado:** Clique no botão azul no topo da tela para abrir o formulário completo (título, descrição, solicitante, técnico responsável, categoria, prioridade e SLA).
   * **Visualização Kanban:** Os cartões são distribuídos automaticamente nas colunas de prioridade correspondentes (*P1 - Crítica*, *P2 - Alta*, *P3 - Média*, *P4 - Baixa*).
   * **Status & Conclusão:** Utilize o seletor de status em cada card. Ao selecionar **Concluído**, uma janela interativa exigirá a descrição da solução aplicada, e o card será minimizado automaticamente.
   * **Gestão Completa:** Utilize os ícones no card para editar as informações ou excluir o chamado de forma segura.

---

## 🛑 Como Parar a Aplicação

Para encerrar os serviços do container mantendo a persistência dos dados, execute:
```bash
docker compose down
```