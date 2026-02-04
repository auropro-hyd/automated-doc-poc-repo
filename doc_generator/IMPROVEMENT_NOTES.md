# Documentation Generator - Improvement Notes

This file tracks known issues and planned improvements for the documentation generator.

## Current Accuracy: ~65%

---

## 🔴 CRITICAL: Mermaid Syntax Errors

### Issue
Mermaid diagrams show "Syntax error in text" in the browser (Mermaid version 11.12.2).

### Root Cause
LLM generates invalid Mermaid syntax:

| Line | Current Code | Issue | Fix |
|------|--------------|-------|-----|
| Class diagram | `OrdersApi --|> OrderServices : uses` | `--|>` is inheritance, not dependency | Use `..>` |
| Class diagram | `Order "1" *-- "many" OrderItem` | Multiplicity not supported | Remove multiplicity |

### Solution Plan

**Option 1: Post-Processing Validation (Recommended)**
```python
def validate_mermaid_syntax(content: str) -> str:
    # Fix relationship syntax
    content = content.replace('--|> ', '..> ')
    # Fix multiplicity notation
    content = re.sub(r'"(\d+)" \*-- "(\w+)"', r'*--', content)
    return content
```

**Option 2: Better LLM Prompts**
```
When generating Mermaid classDiagram:
- Use ..> for dependency (uses)
- Use --|> for inheritance (extends)
- Use *-- for composition
- Do NOT use multiplicity notation like "1" *-- "many"
```

**Option 3: Simpler Diagrams**
Use basic syntax that's less error-prone.

### Trigger
Execute when user says: "Fix Mermaid syntax errors" or "Fix diagram issues"

### ✅ What Works Well
- API Endpoints: 100% accurate
- Key Classes: 80% accurate
- Database/EventBus info: Correct
- Overall structure: Good

---

## 🔧 Improvements Needed (Phase 2)

### 1. Missing Domain Events
The generated documentation should list all domain events:
- OrderStartedDomainEvent
- OrderStatusChangedToAwaitingValidationDomainEvent
- OrderStatusChangedToStockConfirmedDomainEvent
- OrderStatusChangedToPaidDomainEvent
- OrderShippedDomainEvent
- OrderCancelledDomainEvent
- BuyerPaymentMethodVerifiedDomainEvent

**Solution:** Update prompt to specifically ask for domain events list.

### 2. Missing Commands
All commands should be documented:
- CreateOrderCommand
- CreateOrderDraftCommand
- CancelOrderCommand
- ShipOrderCommand
- SetAwaitingValidationOrderStatusCommand
- SetPaidOrderStatusCommand
- SetStockConfirmedOrderStatusCommand
- SetStockRejectedOrderStatusCommand
- IdentifiedCommand (wrapper for idempotency)

**Solution:** Update prompt to specifically ask for commands list.

### 3. Order Status State Machine
Document the complete status flow:
```
Submitted → AwaitingValidation → StockConfirmed → Paid → Shipped
                    ↓                    ↓
                Cancelled            Cancelled
```

**Solution:** Add specific prompt for state machine diagram.

### 4. MediatR Behaviors
Document pipeline behaviors:
- LoggingBehavior
- ValidatorBehavior
- TransactionBehavior

**Solution:** Update prompt to ask about middleware/behaviors.

### 5. Integration Events
List all 13 integration events for cross-service communication.

**Solution:** Specific prompt for integration events.

### 6. Inaccurate .NET Version
- Generated doc says: .NET 6
- Actual version: .NET 9.0

**Solution:** Parse .csproj file for actual version.

### 7. Order Class Properties
Current diagram is simplified. Should include:
- OrderDate
- Address (Value Object)
- OrderStatus
- BuyerId
- PaymentId
- Description
- All status transition methods

**Solution:** More detailed class diagram prompt.

---

## 📋 Implementation Plan for Phase 2

1. **Enhanced Prompts**
   - Create separate prompts for domain events, commands, state machines
   - More specific instructions for class diagrams

2. **Code Analysis**
   - Parse .csproj for .NET version
   - Extract enum values for status types
   - Identify all files with "Event" or "Command" in name

3. **Multi-Pass Generation**
   - First pass: Overview and endpoints
   - Second pass: Domain events and commands
   - Third pass: Diagrams and relationships

4. **Validation Step**
   - Compare generated content against source code
   - Flag missing items
   - Auto-correct known issues

---

## 🗓️ When to Implement

Implement these improvements when user requests:
- "Improve documentation quality"
- "Add more details"
- "Phase 2 improvements"
- "Fix missing items"

---

*Last updated: 2026-02-04*
