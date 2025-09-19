(# Workspace analysis
Generated diagrams and per-project class/interface mappings.

## Requirements checklist

- [x] Analyze all project metadata (.csproj and related) and determine dependency order (bottom-up)
- [x] Create a TD Mermaid diagram showing project dependencies (bottom = no workspace deps)
- [x] Create one LR Mermaid diagram per project showing classes/interfaces and cross-project implementations
- [x] Do not use `.github` or `docs` folders for source content

---

## 1. Project dependency diagram (TD)

The graph is TD (bottom = projects with no workspace dependencies). Arrows point upward from dependency -> dependent.

```mermaid
flowchart TD
	subgraph Layer0["No workspace dependencies (bottom)"]
		SDEF["eShop.ServiceDefaults"]
		EVBUS["EventBus"]
		OD["Ordering.Domain"]
		WCOMP["WebAppComponents"]
		CLIENT["ClientApp"]
	end
	subgraph Layer1["Libraries depending on Layer0"]
		EVB_RMQ["EventBusRabbitMQ"]
		IELOG["IntegrationEventLogEF"]
	end
	subgraph Layer2["Infrastructure / Worker projects"]
		OINF["Ordering.Infrastructure"]
		PROC["OrderProcessor"]
		PAY["PaymentProcessor"]
	end
	subgraph Layer3["APIs / Apps"]
		BASK["Basket.API"]
		CATA["Catalog.API"]
		ORDAPI["Ordering.API"]
		WHAPI["Webhooks.API"]
		MOBILE["Mobile.Bff.Shopping"]
		IDAPI["Identity.API"]
		WEBAPP["WebApp"]
		WEBHOOKCLIENT["WebhookClient"]
	end
	subgraph Layer4["Composition / Host (top)"]
		APPhost["eShop.AppHost"]
	end

	SDEF --> BASK
	SDEF --> CATA
	SDEF --> PROC
	SDEF --> PAY
	SDEF --> ORDAPI
	SDEF --> WHAPI
	SDEF --> MOBILE
	SDEF --> IDAPI
	SDEF --> WEBAPP
	SDEF --> WEBHOOKCLIENT

	EVBUS --> EVB_RMQ
	EVBUS --> IELOG

	WCOMP --> WEBAPP

	EVB_RMQ --> BASK
	EVB_RMQ --> CATA
	EVB_RMQ --> ORDAPI
	EVB_RMQ --> PROC
	EVB_RMQ --> PAY
	EVB_RMQ --> WHAPI
	EVB_RMQ --> WEBAPP

	IELOG --> CATA
	IELOG --> ORDAPI
	IELOG --> WHAPI
	IELOG --> OINF

	OD --> OINF
	OINF --> ORDAPI

	PROC --> APPhost
	PAY --> APPhost

	BASK --> APPhost
	CATA --> APPhost
	ORDAPI --> APPhost
	WHAPI --> APPhost
	MOBILE --> APPhost
	IDAPI --> APPhost
	WEBAPP --> APPhost
	WEBHOOKCLIENT --> APPhost
```