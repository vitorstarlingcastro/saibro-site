# saibro.app.br

Site público do Saibro. Estático, sem build de framework.

- `index.html` — landing. É o export "bundled" do Claude Design (fontes e script embutidos, desempacota no load). Pra atualizar, exportar de novo e sobrescrever o arquivo — o `<title>`, `lang="pt-BR"` e o favicon ficam no head do template interno.
- `termos/`, `privacidade/`, `excluir-conta/` — páginas legais (Termos de Uso, Política de Privacidade e o passo a passo de exclusão de conta que a loja exige). **Geradas**: a fonte é `src/*.md`, e `python src/build.py` reescreve os três `index.html`. Com `--dart <caminho>` regenera também o `legal_content.dart` do app (repo `apptenis-monorepo`), pra site e app nunca divergirem. Mudar o texto = mudar a linha `Versão AAAA-MM-DD` nos dois `.md` + `SAIBRO_POLICY_VERSION` (backend) e `SupabaseConfig.policyVersion` (app).
- Hospedagem: GitHub Pages (branch `main`, raiz). `CNAME` aponta pra `saibro.app.br`.
- DNS (Registro.br): 4 registros `A` pros IPs do GitHub Pages (185.199.108.153, .109.153, .110.153, .111.153) + `CNAME www` → `vitorstarlingcastro.github.io`.
