# saibro.app.br

Página "em breve" do Saibro. Estático, sem build: só `index.html`.

- `index.html` é o export "bundled" do Claude Design (fontes e script embutidos, desempacota no load). Pra atualizar, exportar de novo e sobrescrever o arquivo — o `<title>`, `lang="pt-BR"` e o favicon ficam no head do template interno.
- Hospedagem: GitHub Pages (branch `main`, raiz). `CNAME` aponta pra `saibro.app.br`.
- DNS (Registro.br): 4 registros `A` pros IPs do GitHub Pages (185.199.108.153, .109.153, .110.153, .111.153) + `CNAME www` → `vitorstarlingcastro.github.io`.