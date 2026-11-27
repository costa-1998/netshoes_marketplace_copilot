import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
DAYS = 14
END_DATE = date(2026, 11, 27)
OUT_DIR = Path("tests/fixtures")

SELLERS = [
    {
        "id_seller": "10024",
        "nome_seller": "Mary Jane Calçados",
        "nota_reputacao": 4.8,
        "contato_nome": "Mariana Silva",
        "contato_telefone": "5511998877665",
        "contato_email": "mariana@maryjane.com.br",
        "percentual_de_comissao": 0.20,
    },
    {
        "id_seller": "10026",
        "nome_seller": "Futebol Shop Oficial",
        "nota_reputacao": 4.2,
        "contato_nome": "Carlos Mendes",
        "contato_telefone": "5511987654321",
        "contato_email": "carlos@futebolshop.com.br",
        "percentual_de_comissao": 0.18,
    },
    {
        "id_seller": "14861",
        "nome_seller": "Shihan Artigos Esportivos",
        "nota_reputacao": 4.6,
        "contato_nome": "Antonio Toledo",
        "contato_telefone": "5511982215658",
        "contato_email": "antonio@shihan.com.br",
        "percentual_de_comissao": 0.19,
    },
    {
        "id_seller": "30844",
        "nome_seller": "Use Best Fit",
        "nota_reputacao": 4.9,
        "contato_nome": "Gisele Correia",
        "contato_telefone": "5511996015340",
        "contato_email": "gisele@usebestfit.com.br",
        "percentual_de_comissao": 0.20,
    },
    {
        "id_seller": "11562",
        "nome_seller": "Canguri Bikes",
        "nota_reputacao": 3.9,
        "contato_nome": "David Rocha",
        "contato_telefone": "5511984952664",
        "contato_email": "david@canguribikes.com.br",
        "percentual_de_comissao": 0.16,
    },
]

CATALOG_TEMPLATES = {
    "10024": [
        (
            "C79-1588-010",
            "C79-1588-010-38",
            "Tênis MJ2000 Feminino Branco - Tam 38",
            "Calçados",
            399.90,
            349.90,
            349.90,
            112.00,
            3,
            2,
            2,
            12.90,
            False,
            0.88,
            "ruptura_a",
        ),
        (
            "C79-1588-010",
            "C79-1588-010-37",
            "Tênis MJ2000 Feminino Branco - Tam 37",
            "Calçados",
            399.90,
            349.90,
            349.90,
            112.00,
            28,
            2,
            2,
            12.90,
            False,
            0.85,
            "campeao",
        ),
        (
            "C79-1454-006",
            "C79-1454-006-37",
            "Tênis Mary Jane Insta 2.0 Preto - Tam 37",
            "Calçados",
            199.90,
            143.92,
            139.90,
            40.30,
            30,
            4,
            2,
            14.90,
            True,
            0.08,
            "trava_1p",
        ),
        (
            "C79-1454-006",
            "C79-1454-006-35",
            "Tênis Mary Jane Insta 2.0 Preto - Tam 35",
            "Calçados",
            199.90,
            143.92,
            143.92,
            40.30,
            24,
            6,
            2,
            19.90,
            False,
            0.15,
            "gargalo_prazo",
        ),
        (
            "C79-160B-004",
            "C79-160B-004-36",
            "Tênis High School 2.0 Rosa - Tam 36",
            "Calçados",
            329.90,
            289.90,
            259.90,
            86.97,
            45,
            3,
            3,
            11.90,
            False,
            0.18,
            "oportunidade_preco",
        ),
        (
            "C79-160B-004",
            "C79-160B-004-39",
            "Tênis High School 2.0 Rosa - Tam 39",
            "Calçados",
            329.90,
            264.90,
            259.90,
            72.00,
            20,
            3,
            3,
            11.90,
            False,
            0.55,
            "estavel",
        ),
        (
            "C79-1538-018",
            "C79-1538-018-39",
            "Tênis Mary Jane Challenger Bege - Tam 39",
            "Calçados",
            219.90,
            172.42,
            172.42,
            43.11,
            60,
            3,
            3,
            14.90,
            False,
            0.75,
            "cauda_longa",
        ),
        (
            "C79-1455-006",
            "C79-1455-006-34",
            "Tênis Challenger Feminino Preto - Tam 34",
            "Calçados",
            229.90,
            179.90,
            169.90,
            45.00,
            35,
            4,
            2,
            15.90,
            False,
            0.25,
            "oportunidade_preco",
        ),
        (
            "C79-1455-006",
            "C79-1455-006-40",
            "Tênis Challenger Feminino Preto - Tam 40",
            "Calçados",
            229.90,
            172.42,
            172.42,
            42.00,
            2,
            2,
            2,
            12.90,
            False,
            0.80,
            "ruptura_a",
        ),
        (
            "C79-1700-001",
            "C79-1700-001-36",
            "Bota Coturno Mary Jane Tratorada - Tam 36",
            "Calçados",
            299.90,
            249.90,
            239.90,
            70.00,
            18,
            3,
            3,
            13.90,
            False,
            0.42,
            "checkout_drop",
        ),
        (
            "C79-1700-001",
            "C79-1700-001-37",
            "Bota Coturno Mary Jane Tratorada - Tam 37",
            "Calçados",
            299.90,
            249.90,
            249.90,
            70.00,
            22,
            3,
            3,
            13.90,
            False,
            0.68,
            "estavel",
        ),
        (
            "C79-1810-002",
            "C79-1810-002-UN",
            "Mochila Casual Mary Jane Nylon - Único",
            "Acessórios",
            159.90,
            119.90,
            119.90,
            32.00,
            50,
            5,
            2,
            18.90,
            False,
            0.20,
            "gargalo_prazo",
        ),
        (
            "C79-1820-005",
            "C79-1820-005-UN",
            "Meia Invisível Kit 3 Pares - Único",
            "Acessórios",
            49.90,
            39.90,
            39.90,
            10.00,
            120,
            2,
            2,
            9.90,
            False,
            0.90,
            "cauda_longa",
        ),
        (
            "C79-1900-012",
            "C79-1900-012-38",
            "Tênis Slip On Casual Cinza - Tam 38",
            "Calçados",
            189.90,
            149.90,
            139.90,
            36.00,
            40,
            3,
            3,
            12.90,
            True,
            0.05,
            "trava_1p",
        ),
        (
            "C79-1900-012",
            "C79-1900-012-36",
            "Tênis Slip On Casual Cinza - Tam 36",
            "Calçados",
            189.90,
            149.90,
            139.90,
            36.00,
            32,
            3,
            3,
            12.90,
            False,
            0.22,
            "oportunidade_preco",
        ),
    ],
    "10026": [
        (
            "206-9972-026",
            "206-9972-026-P",
            "Body Corinthians Infantil Torcida Baby - P",
            "Roupas",
            99.90,
            89.90,
            74.90,
            31.47,
            50,
            2,
            2,
            12.90,
            False,
            0.22,
            "oportunidade_preco",
        ),
        (
            "206-9972-026",
            "206-9972-026-M",
            "Body Corinthians Infantil Torcida Baby - M",
            "Roupas",
            99.90,
            74.90,
            74.90,
            24.00,
            4,
            2,
            2,
            12.90,
            False,
            0.85,
            "ruptura_a",
        ),
        (
            "30D-0341-060",
            "30D-0341-060-M",
            "Macacão Regata Bebê Palmeiras - M",
            "Roupas",
            99.90,
            59.95,
            59.95,
            15.00,
            15,
            5,
            2,
            16.90,
            False,
            0.40,
            "checkout_drop",
        ),
        (
            "206-0246-068",
            "206-0246-068-4",
            "Conjunto Flamengo Sublimado Infantil - 4",
            "Roupas",
            199.90,
            169.90,
            159.90,
            52.00,
            25,
            3,
            2,
            14.90,
            True,
            0.06,
            "trava_1p",
        ),
        (
            "206-0246-068",
            "206-0246-068-6",
            "Conjunto Flamengo Sublimado Infantil - 6",
            "Roupas",
            199.90,
            159.90,
            159.90,
            48.00,
            20,
            6,
            2,
            19.90,
            False,
            0.14,
            "gargalo_prazo",
        ),
        (
            "50D-3891-178",
            "50D-3891-178-9",
            "Luva Penalty Se7e Training X - Tam 9",
            "Equipamentos",
            179.90,
            159.00,
            159.00,
            49.00,
            30,
            2,
            2,
            11.90,
            False,
            0.82,
            "campeao",
        ),
        (
            "50D-3892-006",
            "50D-3892-006-32",
            "Chuteira Penalty Matis Kids - Tam 32",
            "Calçados",
            189.90,
            159.00,
            139.90,
            44.00,
            38,
            3,
            3,
            12.90,
            False,
            0.19,
            "oportunidade_preco",
        ),
        (
            "D41-0203-792",
            "D41-0203-792-UN",
            "Caneca de Vidro Fluminense 340ml - Único",
            "Equipamentos",
            59.90,
            49.90,
            49.90,
            10.00,
            80,
            3,
            3,
            15.90,
            False,
            0.80,
            "cauda_longa",
        ),
        (
            "D41-0914-060",
            "D41-0914-060-UN",
            "Caneca Térmica Inox Palmeiras 1200ml",
            "Equipamentos",
            189.90,
            159.00,
            159.00,
            50.00,
            2,
            2,
            2,
            13.90,
            False,
            0.86,
            "ruptura_a",
        ),
        (
            "687-345C-030",
            "687-345C-030-G",
            "Camiseta Elite Brasil Masculina - G",
            "Roupas",
            139.90,
            119.00,
            119.00,
            35.00,
            42,
            3,
            3,
            12.90,
            False,
            0.70,
            "estavel",
        ),
        (
            "2JR-0000-006",
            "2JR-0000-006-M",
            "Sunga Slip Pé na Água Preta - M",
            "Acessórios",
            89.90,
            69.90,
            69.90,
            21.00,
            55,
            3,
            3,
            11.90,
            False,
            0.65,
            "estavel",
        ),
        (
            "564-0195-792",
            "564-0195-792-UN",
            "Prancheta Tática Magnética Society",
            "Acessórios",
            179.90,
            152.90,
            152.90,
            46.00,
            19,
            4,
            4,
            14.90,
            False,
            0.72,
            "cauda_longa",
        ),
        (
            "30D-0418-054",
            "30D-0418-054-2",
            "Conjunto Toddler Palmeiras - 2 Anos",
            "Roupas",
            229.90,
            209.00,
            189.90,
            62.00,
            26,
            3,
            2,
            13.90,
            False,
            0.24,
            "oportunidade_preco",
        ),
        (
            "D40-3842-006",
            "D40-3842-006-GG",
            "Camiseta Atlético Mineiro Wag - GG",
            "Roupas",
            139.90,
            119.00,
            119.00,
            34.00,
            33,
            5,
            2,
            17.90,
            False,
            0.16,
            "gargalo_prazo",
        ),
        (
            "206-0358-026",
            "206-0358-026-P",
            "Conjunto Santos Infantil 3 Peças - P",
            "Roupas",
            219.90,
            199.00,
            199.00,
            60.00,
            28,
            3,
            3,
            12.90,
            True,
            0.07,
            "trava_1p",
        ),
    ],
}


def build_catalog_for_seller(seller_id: str) -> list[tuple]:
    if seller_id in CATALOG_TEMPLATES:
        return CATALOG_TEMPLATES[seller_id]
    # Gera 15 SKUs padronizados para os demais sellers
    base_idx = int(seller_id)
    profiles = [
        "campeao",
        "ruptura_a",
        "trava_1p",
        "gargalo_prazo",
        "oportunidade_preco",
        "checkout_drop",
        "estavel",
        "estavel",
        "oportunidade_preco",
        "gargalo_prazo",
        "cauda_longa",
        "cauda_longa",
        "estavel",
        "ruptura_a",
        "trava_1p",
    ]
    items = []
    for idx, prof in enumerate(profiles, start=1):
        pai = f"NS-{base_idx}-{idx:02d}"
        filho = f"{pai}-U"
        p_de = round(149.90 + idx * 15, 2)
        p_por = round(p_de * 0.85, 2)
        win_p = round(p_por * 0.90, 2) if prof == "oportunidade_preco" else p_por
        margem = round(p_por * 0.28, 2)
        est = 2 if prof == "ruptura_a" else random.randint(18, 65)
        prazo = 6 if prof == "gargalo_prazo" else 2
        frete = 19.90 if prof == "gargalo_prazo" else 11.90
        is_1p = prof == "trava_1p"
        bb = 0.06 if is_1p else (0.18 if prof in ("gargalo_prazo", "oportunidade_preco") else 0.82)
        items.append(
            (
                pai,
                filho,
                f"Produto Esportivo {seller_id} #{idx:02d}",
                "Esportes",
                p_de,
                p_por,
                win_p,
                margem,
                est,
                prazo,
                2,
                frete,
                is_1p,
                bb,
                prof,
            )
        )
    return items


def generate() -> None:
    random.seed(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sales_rows: list[dict] = []

    for seller in SELLERS:
        sid = seller["id_seller"]
        comm_pct = seller["percentual_de_comissao"]
        catalog = build_catalog_for_seller(sid)

        for day_offset in range(DAYS):
            cur_date = (END_DATE - timedelta(days=DAYS - 1 - day_offset)).isoformat()
            day_factor = (
                1.15
                if (END_DATE - timedelta(days=DAYS - 1 - day_offset)).weekday() in (0, 1)
                else 0.95
            )

            for item in catalog:
                (
                    sku_pai,
                    sku_filho,
                    nome,
                    cat,
                    p_de,
                    p_por,
                    win_p,
                    margem_unit,
                    est_base,
                    prazo,
                    win_prazo,
                    frete,
                    tem_1p,
                    bb_rate,
                    profile,
                ) = item

                # Volume base por perfil
                if profile in ("campeao", "ruptura_a"):
                    sessoes = int(random.randint(280, 420) * day_factor)
                    conv = random.uniform(0.028, 0.038)
                elif profile in ("oportunidade_preco", "gargalo_prazo", "trava_1p"):
                    sessoes = int(random.randint(180, 320) * day_factor)
                    conv = random.uniform(0.008, 0.015)
                elif profile == "checkout_drop":
                    sessoes = int(random.randint(160, 240) * day_factor)
                    conv = random.uniform(0.006, 0.011)
                elif profile == "cauda_longa":
                    sessoes = random.randint(15, 55)
                    conv = 0.0
                else:
                    sessoes = int(random.randint(120, 210) * day_factor)
                    conv = random.uniform(0.018, 0.025)

                cliques = int(sessoes * random.uniform(0.65, 0.85))
                compras_fat = int(round(cliques * conv))
                unidades = compras_fat

                if profile == "checkout_drop":
                    add_cart = max(compras_fat + 15, int(cliques * 0.22))
                    add_ship = max(compras_fat + 8, int(add_cart * 0.55))
                    add_pay = max(compras_fat + 5, int(add_ship * 0.70))
                    cancelamentos = max(1, int(compras_fat * 0.50))
                else:
                    add_cart = max(compras_fat, int(cliques * random.uniform(0.10, 0.16)))
                    add_ship = max(compras_fat, int(add_cart * random.uniform(0.65, 0.80)))
                    add_pay = max(compras_fat, int(add_ship * random.uniform(0.80, 0.92)))
                    cancelamentos = 1 if compras_fat >= 8 and random.random() < 0.35 else 0

                rec_fat = round(unidades * p_por, 2)
                rec_capt = round(rec_fat * random.uniform(1.03, 1.12), 2) if unidades > 0 else 0.0
                val_comm = round(rec_fat * comm_pct, 2)
                margem_total = round(unidades * margem_unit, 2)
                rentabilidade = round(margem_unit / p_por, 4)

                estoque = (
                    est_base if profile == "ruptura_a" else max(5, est_base - (day_offset % 6))
                )
                vmd = round(max(0.05, compras_fat * random.uniform(0.85, 1.15)), 2)
                cobertura = round(estoque / vmd, 1)
                preco_1p = round(win_p, 2) if tem_1p else ""
                delta_preco = round(p_por - win_p, 2)
                delta_prazo = prazo - win_prazo
                taxa_conv = round(compras_fat / cliques, 4) if cliques > 0 else 0.0

                sales_rows.append(
                    {
                        "data": cur_date,
                        "id_seller": sid,
                        "sku_pai": sku_pai,
                        "sku_filho": sku_filho,
                        "percentual_de_comissao": comm_pct,
                        "nome_produto": nome,
                        "categoria_do_produto": cat,
                        "categoria_curva": "C",  # Recalculado abaixo por Pareto 80-95-100
                        "vmd": vmd,
                        "unidades_vendidas": unidades,
                        "receita_captada": rec_capt,
                        "receita_faturada": rec_fat,
                        "valor_de_comissao": val_comm,
                        "preco_de": p_de,
                        "preco_por": p_por,
                        "preco_1p": preco_1p,
                        "delta_preco": delta_preco,
                        "margem": margem_total,
                        "estoque": estoque,
                        "cobertura": cobertura,
                        "sessoes": sessoes,
                        "cliques": cliques,
                        "adicao_ao_carrinho": add_cart,
                        "adicao_de_pagamento": add_pay,
                        "adicao_de_informacoes_de_envio": add_ship,
                        "compras_faturadas": compras_fat,
                        "cancelamentos": cancelamentos,
                        "prazo_medio_envio": prazo,
                        "delta_prazo": delta_prazo,
                        "custo_frete": frete,
                        "tem_1p": str(tem_1p).lower(),
                        "buybox_win_rate": bb_rate,
                        "winner_avg_price": win_p,
                        "winner_avg_prazo": win_prazo,
                        "rentabilidade": rentabilidade,
                        "taxa_conversao": taxa_conv,
                    }
                )

    # Calcula Curva ABC (80-95-100) sobre a receita_faturada acumulada por seller
    for seller in SELLERS:
        sid = seller["id_seller"]
        s_rows = [r for r in sales_rows if r["id_seller"] == sid]
        sku_rev: dict[str, float] = {}
        for r in s_rows:
            sku_rev[r["sku_filho"]] = sku_rev.get(r["sku_filho"], 0.0) + r["receita_faturada"]

        total_rev = sum(sku_rev.values()) or 1.0
        sorted_skus = sorted(sku_rev.items(), key=lambda x: x[1], reverse=True)
        cum = 0.0
        sku_curve: dict[str, str] = {}
        for sku, rev in sorted_skus:
            cum += rev / total_rev
            if cum <= 0.80:
                sku_curve[sku] = "A"
            elif cum <= 0.95:
                sku_curve[sku] = "B"
            else:
                sku_curve[sku] = "C"

        for r in s_rows:
            r["categoria_curva"] = sku_curve[r["sku_filho"]]

    # Grava seller_sku_sales.csv
    sales_path = OUT_DIR / "seller_sku_sales.csv"
    with sales_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(sales_rows[0].keys()))
        writer.writeheader()
        writer.writerows(sales_rows)

    # Consolida e grava seller_master.csv
    master_rows = []
    for seller in SELLERS:
        sid = seller["id_seller"]
        s_rows = [r for r in sales_rows if r["id_seller"] == sid]
        tot_cliques = sum(r["cliques"] for r in s_rows)
        tot_compras = sum(r["compras_faturadas"] for r in s_rows)
        tot_rec = sum(r["receita_faturada"] for r in s_rows)
        tot_margem = sum(r["margem"] for r in s_rows)

        master_rows.append(
            {
                **seller,
                "rentabilidade": round(tot_margem / tot_rec, 4) if tot_rec > 0 else 0.0,
                "taxa_conversao": round(tot_compras / tot_cliques, 4) if tot_cliques > 0 else 0.0,
            }
        )

    master_cols = [
        "id_seller",
        "nome_seller",
        "nota_reputacao",
        "contato_nome",
        "contato_telefone",
        "contato_email",
        "rentabilidade",
        "taxa_conversao",
        "percentual_de_comissao",
    ]
    master_path = OUT_DIR / "seller_master.csv"
    with master_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=master_cols)
        writer.writeheader()
        writer.writerows(master_rows)

    print(f"Gerados: {len(master_rows)} sellers em {master_path}")
    print(f"Gerados: {len(sales_rows)} registros diários em {sales_path}")


if __name__ == "__main__":
    generate()
