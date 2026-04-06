# PRODUCT REQUIREMENTS DOCUMENT
## Integrated Point of Sale System: Cafe/Restaurant & Hotel
### Prepared for: Developer Team & Investors
### Version: 1.0 | Date: April 2026 | Market: Kenya

---

> **Document Scope:** This document contains two full Product Requirements Documents (PRDs):
> - **PRD 1:** Cafe & Restaurant POS System
> - **PRD 2:** Hotel POS & Room Ordering System
>
> Both systems are designed to work as standalone products and as an integrated suite. All requirements are tailored to the Kenyan market, KRA eTIMS/TIMS compliance, M-Pesa payment infrastructure, and local operational realities including unreliable power and variable internet connectivity.

---

---

# PRD 1: CAFE & RESTAURANT POS SYSTEM

---

## 1. Executive Summary

This document defines the requirements for a **waiter-operated, touchscreen-based Point of Sale (POS) system** designed for cafes and restaurants operating in Kenya. The system addresses the unique demands of the Kenyan hospitality market: KRA eTIMS fiscal compliance, M-Pesa payment integration, offline resilience for power and internet outages, and modern operational intelligence including AI-powered upselling and real-time cloud dashboards.

The system is operated exclusively by trained waitstaff on shared touchscreen tablets and fixed terminal stations — not by customers. This waiter-centric model ensures order accuracy, upsell opportunity, and staff accountability while preserving the human service experience central to Kenyan hospitality culture.

**Target Delivery:** 12-month phased build
**Primary Users:** Waiters, Cashiers, Kitchen Staff, Managers, Owners
**Core Integration Points:** KRA eTIMS API, M-Pesa Daraja API, Kitchen Display System (KDS), Cloud Analytics Dashboard

---

## 2. Business Context

### 2.1 Target Business Profile

| Attribute             | Detail                                                       |
|-----------------------|--------------------------------------------------------------|
| Business Type         | Cafe, Casual Dining Restaurant, or Combined Cafe/Restaurant  |
| Location              | Kenya (urban, peri-urban)                                    |
| Scale                 | 5–150 seats; 1–5 branches                                    |
| Staff Count           | 3–30 employees                                               |
| Daily Transactions    | 50–600 orders per day                                        |
| Primary Payment       | Cash, M-Pesa, Card                                           |

### 2.2 Market Context & Challenges

Kenya's food service industry is among East Africa's fastest-growing sectors. However, restaurant operators face a distinct set of operational challenges that any viable POS solution must address:

| Challenge                     | Impact on POS Design                                                   |
|-------------------------------|-------------------------------------------------------------------------|
| Frequent power outages (KPLC load shedding) | System must run on battery-backed hardware; offline mode mandatory |
| Variable internet connectivity | All core functions must work offline; sync when connectivity restored   |
| KRA eTIMS compliance mandate  | Every sale must generate a compliant digital fiscal receipt             |
| M-Pesa dominance in payments  | STK Push integration is non-negotiable; 70%+ of digital payments via M-Pesa |
| High staff turnover           | UI must be learnable in under 2 hours; PIN-based login on shared devices |
| Multi-currency considerations | KES primary; USD accepted in tourist-facing establishments              |
| VAT 16% on all food services  | Automated VAT calculation and KRA reporting required                    |

### 2.3 Ordering Model

**CRITICAL DESIGN CONSTRAINT:** This is a **waiter-operated system only.** Customers do not interact with the POS or ordering tablets at any point. Waiters approach the table, take verbal orders from customers, and enter the order on a shared tablet or terminal. This model was chosen deliberately to:
- Maintain the quality of human service interaction
- Reduce customer-facing technology friction
- Maintain waiter accountability for upsells and order accuracy
- Comply with local labor norms (waiter employment is central to the hospitality economy)

---

## 3. User Personas

### Persona 1: The Waiter / Server

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Name           | Amina, 24                                                              |
| Role           | Full-time waitress at a Nairobi cafe                                   |
| Tech Comfort   | Moderate; uses Android smartphone daily                                |
| Goal           | Take orders fast, avoid mistakes, earn tips through good service       |
| Pain Points    | Slow systems during lunch rush; unclear order status; forgotten modifiers |
| Needs from POS | Fast PIN login; clear table map; quick category navigation; one-tap send to kitchen |

### Persona 2: The Cashier

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Name           | Brian, 30                                                              |
| Role           | Cashier at busy restaurant                                             |
| Tech Comfort   | Moderate-high                                                          |
| Goal           | Process payments fast; avoid cash errors; issue proper receipts        |
| Pain Points    | M-Pesa confirmation delays; split bill confusion; till reconciliation  |
| Needs from POS | Multi-payment processing; till management; ETR receipt printing        |

### Persona 3: Kitchen Staff / Chef

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Name           | Samuel, 35                                                             |
| Role           | Line cook                                                              |
| Tech Comfort   | Low                                                                    |
| Goal           | See orders clearly; know preparation priority; mark items as done      |
| Pain Points    | Illegible handwritten tickets; lost orders; no awareness of table priority |
| Needs from POS | Large-font KDS display; order timers; clear item modifiers; bump button |

### Persona 4: Manager / Shift Supervisor

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Name           | Grace, 38                                                              |
| Role           | Restaurant Manager                                                     |
| Tech Comfort   | High                                                                   |
| Goal           | Monitor performance; manage voids; ensure compliance; handle complaints |
| Pain Points    | Staff abusing voids; no real-time visibility from office               |
| Needs from POS | Manager approval flow; live dashboard on phone; void audit trail       |

### Persona 5: Owner / Multi-Branch Director

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Name           | David, 45                                                              |
| Role           | Owner of 3-branch cafe chain                                           |
| Tech Comfort   | Moderate                                                               |
| Goal           | Profitability oversight; tax compliance; staff accountability          |
| Pain Points    | No visibility across branches; inconsistent stock management           |
| Needs from POS | Cloud dashboard; consolidated reports; KRA filing support              |

---

## 4. Core Functional Requirements

### 4.1 Authentication & Session Management

| Req ID  | Requirement                                                                            | Priority |
|---------|----------------------------------------------------------------------------------------|----------|
| AUTH-01 | Waiter logs in with a unique 4–6 digit PIN on a shared tablet                          | Must Have |
| AUTH-02 | Session auto-locks after 3 minutes of inactivity; re-entry requires PIN               | Must Have |
| AUTH-03 | Role-based access: Waiter, Cashier, Manager, Admin, Owner (each with defined permissions) | Must Have |
| AUTH-04 | Manager override PIN for restricted actions (voids, discounts, refunds)                | Must Have |
| AUTH-05 | Biometric login option (fingerprint) on supported devices as secondary method          | Should Have |
| AUTH-06 | Failed PIN attempts (5x) lock the device and alert manager                             | Must Have |
| AUTH-07 | All actions logged with waiter ID and timestamp for audit trail                        | Must Have |

### 4.2 Table Management

| Req ID  | Requirement                                                                            | Priority |
|---------|----------------------------------------------------------------------------------------|----------|
| TABLE-01 | Interactive floor map view showing all tables with real-time status (Available / Occupied / Reserved / Bill Requested) | Must Have |
| TABLE-02 | Waiter selects table from floor map to open or access an order                        | Must Have |
| TABLE-03 | Tables color-coded: Green (available), Red (occupied), Yellow (bill pending), Blue (reserved) | Must Have |
| TABLE-04 | Manager can configure floor map layout (add/remove/rename tables, set sections)        | Must Have |
| TABLE-05 | Merge two or more tables into one combined order                                       | Must Have |
| TABLE-06 | Transfer an order from one table to another (table change mid-meal)                    | Must Have |
| TABLE-07 | Cover count entry per table (number of guests seated)                                  | Should Have |
| TABLE-08 | Table occupancy timer displayed on floor map (how long table has been occupied)        | Should Have |
| TABLE-09 | Section assignment: Waiter A owns Section 1, Waiter B owns Section 2                  | Should Have |

### 4.3 Order Taking

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| ORDER-01 | Menu displayed in clearly categorized tabs (e.g., Breakfast, Mains, Drinks, Desserts, Specials) | Must Have |
| ORDER-02 | High-quality item images displayed alongside name and price                           | Must Have |
| ORDER-03 | Waiter taps item to add to order; quantity adjustable with +/- buttons                | Must Have |
| ORDER-04 | Item modifier system: select extras, removals, cooking preferences (e.g., "no onions", "extra sauce", "well done") | Must Have |
| ORDER-05 | Free-text notes field per item for special instructions                               | Must Have |
| ORDER-06 | Items grouped by seat/guest number within the same table order                        | Should Have |
| ORDER-07 | Waiter can add items to an already-open order (open tab model)                        | Must Have |
| ORDER-08 | "Fire" button sends order to kitchen immediately; "Hold" queues for later             | Must Have |
| ORDER-09 | Course sequencing: Starter / Main / Dessert — kitchen fires courses in sequence       | Should Have |
| ORDER-10 | Unavailable items greyed out and marked "86'd" (out of stock)                         | Must Have |
| ORDER-11 | Waiter sees real-time kitchen status: "In Preparation", "Ready", "Served"             | Must Have |
| ORDER-12 | AI upsell prompts shown to waiter after item selection (e.g., "Customers who order this also add...") | Nice to Have |
| ORDER-13 | Popular items and top-sellers highlighted on menu screen                              | Should Have |

### 4.4 Kitchen Communication

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| KIT-01   | Orders sent electronically to Kitchen Display System (KDS) screen in kitchen          | Must Have |
| KIT-02   | Kitchen receipt printer (thermal) as fallback if KDS is unavailable                   | Must Have |
| KIT-03   | KDS displays: table number, waiter name, items, modifiers, time order was placed       | Must Have |
| KIT-04   | Order timer shows elapsed time; turns amber at 10 min, red at 20 min                  | Must Have |
| KIT-05   | Kitchen can "bump" (mark ready) individual items or entire orders                     | Must Have |
| KIT-06   | Modifications shown in bold/highlighted color on KDS for visibility                   | Must Have |
| KIT-07   | KDS supports order routing by station: Grill orders go to grill screen, drinks to bar screen | Should Have |
| KIT-08   | AI-powered prep time prediction shown on KDS per item based on historical data        | Nice to Have |
| KIT-09   | Kitchen load balancing: KDS shows total active orders and estimated kitchen queue time | Should Have |
| KIT-10   | Audible alert on KDS when new order arrives                                            | Must Have |

### 4.5 Billing & Payment

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| PAY-01   | Bill generated from open order at any time; waiter prints or displays on tablet       | Must Have |
| PAY-02   | Split bill by item: assign specific items to different guests                         | Must Have |
| PAY-03   | Split bill equally: divide total by number of guests                                  | Must Have |
| PAY-04   | Split bill by custom amount                                                            | Must Have |
| PAY-05   | Accept payment: Cash, M-Pesa (STK Push), Card (integrated terminal), Room Charge      | Must Have |
| PAY-06   | Mixed payment: partial M-Pesa + partial cash                                           | Must Have |
| PAY-07   | Cash payment: system calculates change due                                             | Must Have |
| PAY-08   | M-Pesa STK Push: waiter enters customer phone number; push sent to customer's phone   | Must Have |
| PAY-09   | M-Pesa payment confirmation displayed on POS within 30 seconds; auto-retry on timeout | Must Have |
| PAY-10   | Card payment via integrated card terminal (Visa, Mastercard, local debit)             | Must Have |
| PAY-11   | Discount application: percentage or fixed amount; requires manager PIN above threshold | Must Have |
| PAY-12   | Void an item or entire order before payment; manager PIN required                     | Must Have |
| PAY-13   | Refund processing post-payment with audit trail and manager approval                  | Must Have |
| PAY-14   | Room charge posting for hotel guests (if integrated with Hotel POS PRD 2)             | Should Have |
| PAY-15   | Loyalty points: accumulate per transaction; redeem at point of payment                | Should Have |
| PAY-16   | Corporate/company account billing with purchase order reference                        | Should Have |

### 4.6 Receipt Management

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| REC-01   | KRA eTIMS compliant digital fiscal receipt generated for every completed transaction  | Must Have |
| REC-02   | Receipt includes: business name, PIN, ETR serial number, eTIMS QR code, itemized list, VAT breakdown, total, payment method | Must Have |
| REC-03   | Physical receipt printed on thermal printer (80mm standard)                           | Must Have |
| REC-04   | Digital receipt sent via: WhatsApp (preferred in Kenya), SMS, or email                | Should Have |
| REC-05   | Customer can choose receipt delivery method at point of payment                       | Should Have |
| REC-06   | Kitchen receipt printed separately from customer receipt                              | Must Have |

---

## 5. Kenya Compliance Requirements

### 5.1 KRA eTIMS Integration

The Kenya Revenue Authority's **Electronic Tax Invoice Management System (eTIMS)** is mandatory for all VAT-registered businesses effective January 2024. Restaurants are high-priority enforcement targets.

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| TAX-01   | eTIMS system-to-system integration via OSCU (Online Sales Control Unit) or VSCU (Virtual Sales Control Unit) API | Must Have |
| TAX-02   | Every completed sale generates a signed digital tax invoice transmitted to KRA in real time | Must Have |
| TAX-03   | Offline invoice queue: invoices stored locally when offline; batch-transmitted when connectivity is restored | Must Have |
| TAX-04   | Each receipt displays KRA-assigned QR code verifiable at itax.kra.go.ke               | Must Have |
| TAX-05   | eTIMS invoice numbering system (sequential, non-repeatable, KRA-compliant)            | Must Have |
| TAX-06   | Receipt must include: Trader name, KRA PIN, eTIMS serial, date/time, itemized prices, VAT amount, total | Must Have |
| TAX-07   | System certified as a Trader Invoicing System (TIS) through KRA approval process      | Must Have |
| TAX-08   | Sandbox testing environment configured against KRA's test environment (https://etims-sbx.kra.go.ke) | Must Have |

### 5.2 VAT Calculation & Reporting

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| VAT-01   | All VATable items automatically calculate 16% VAT (VAT-inclusive pricing model)       | Must Have |
| VAT-02   | VAT-exempt items (e.g., basic foodstuffs per KRA schedule) flagged separately in menu | Must Have |
| VAT-03   | VAT breakdown displayed on every receipt: VAT-exclusive subtotal + VAT amount + Total | Must Have |
| VAT-04   | Monthly VAT report generated in KRA-compatible format for filing via iTax             | Must Have |
| VAT-05   | VAT Registration Number (VRN) displayed on all receipts                               | Must Have |

### 5.3 Fiscal Reports

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| RPT-TAX-01 | **Z-Report:** End-of-day sales totals, VAT summary, payment method breakdown — auto-generated at close of business | Must Have |
| RPT-TAX-02 | **X-Report:** Mid-day interim report without resetting counters                       | Must Have |
| RPT-TAX-03 | Reports exportable as PDF and CSV for accountant submission                           | Must Have |
| RPT-TAX-04 | Historical report archive: minimum 7 years retention (KRA requirement)                | Must Have |

---

## 6. Payment Integration

### 6.1 M-Pesa Daraja API

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| MPESA-01 | Integration with Safaricom Daraja API for M-Pesa Express (STK Push / Lipa Na M-Pesa) | Must Have |
| MPESA-02 | Waiter enters customer's Safaricom phone number; STK Push initiated from POS           | Must Have |
| MPESA-03 | Customer receives payment prompt on their phone; enters PIN to confirm                | Must Have |
| MPESA-04 | POS polls M-Pesa callback URL and displays confirmation within 30 seconds             | Must Have |
| MPESA-05 | M-Pesa transaction reference (receipt code) stored against the order and printed on receipt | Must Have |
| MPESA-06 | Automatic retry if initial STK Push times out (with customer consent)                 | Should Have |
| MPESA-07 | C2B (Customer to Business) support via PayBill number for walk-in counter payments    | Should Have |
| MPESA-08 | M-Pesa reconciliation report: daily list of all M-Pesa transactions with codes        | Must Have |
| MPESA-09 | Support for M-Pesa Till Number and PayBill Number (both models)                        | Must Have |
| MPESA-10 | Test environment integration with Daraja Sandbox before go-live                        | Must Have |

### 6.2 Card Payments

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| CARD-01  | Integration with PCI-DSS compliant card terminal (Visa, Mastercard, Amex)            | Must Have |
| CARD-02  | Support for chip-and-PIN, contactless NFC, and magnetic stripe                        | Must Have |
| CARD-03  | Card terminal connected via Bluetooth or USB to POS terminal                          | Must Have |
| CARD-04  | Payment amount auto-sent to card terminal from POS (no manual re-entry)               | Must Have |
| CARD-05  | Card payment confirmation auto-captured and attached to order                          | Must Have |
| CARD-06  | Recommended Partners: KCB Merchant Services, Equity Bank POS, DPO Group, Pesapal     | Should Have |

### 6.3 Cash Handling & Till Management

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| CASH-01  | Cash drawer connected to receipt printer; opens on cash payment completion             | Must Have |
| CASH-02  | Opening float entry at start of shift (cashier declares starting cash)                | Must Have |
| CASH-03  | Till reconciliation at end of shift: system expected vs. physical count                | Must Have |
| CASH-04  | Cash drops (mid-shift cash removal to safe) logged in system with manager approval    | Must Have |
| CASH-05  | Petty cash expenses logged against till                                                | Should Have |
| CASH-06  | Shortage/overage report per cashier per shift                                          | Must Have |

---

## 7. Inventory & Menu Management

### 7.1 Menu Configuration

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| MENU-01  | Admin creates/edits menu items: name, description, image, category, price, VAT flag   | Must Have |
| MENU-02  | Menu items organized into categories and sub-categories with drag-and-drop ordering   | Must Have |
| MENU-03  | Item availability toggle: instantly mark item as available or unavailable (86'd)       | Must Have |
| MENU-04  | Scheduled availability: breakfast items only visible 6am–11am; etc.                   | Should Have |
| MENU-05  | Modifier groups: define extras (e.g., "Milk Type": Full Fat / Almond / Oat)           | Must Have |
| MENU-06  | Price override per outlet or per time period (happy hour pricing)                     | Should Have |
| MENU-07  | Bundle/combo items with composite pricing                                              | Should Have |
| MENU-08  | Menu item images synced from cloud; displayed on waiter tablet at 1:1 ratio           | Should Have |
| MENU-09  | Multi-branch: different menus per branch with shared item master                       | Should Have |

### 7.2 Inventory Management

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| INV-01   | Recipe-based inventory: each menu item linked to ingredient quantities (e.g., 1 Cappuccino = 18g coffee + 180ml milk) | Must Have |
| INV-02   | Automatic inventory deduction on each sale based on recipe                             | Must Have |
| INV-03   | Real-time stock levels visible to manager dashboard                                    | Must Have |
| INV-04   | Low stock alerts: notification when ingredient falls below reorder point               | Must Have |
| INV-05   | Stock receiving module: record new stock deliveries with supplier and quantity         | Must Have |
| INV-06   | Waste tracking: manual waste entries with reason code                                  | Must Have |
| INV-07   | Variance report: theoretical stock vs. physical count                                  | Must Have |
| INV-08   | Supplier management: track suppliers, contact info, delivery schedules                | Should Have |
| INV-09   | Purchase order generation for restock based on PAR levels                              | Should Have |
| INV-10   | AI-powered restock prediction: suggests order quantities based on sales velocity and historical demand | Nice to Have |

---

## 8. Reporting & Analytics

### 8.1 Operational Reports

| Report Name               | Description                                              | Frequency     | User         |
|---------------------------|----------------------------------------------------------|---------------|--------------|
| Daily Sales Summary       | Total revenue, covers, average spend, by payment method  | Daily         | Manager/Owner |
| Sales by Waiter           | Revenue and order count per waiter per shift             | Daily/Weekly  | Manager      |
| Sales by Category/Item    | Best-selling and worst-selling items                     | Daily/Weekly  | Manager/Owner |
| Hourly Revenue Heatmap    | Revenue by hour of day (identifies peak periods)         | Weekly        | Manager/Owner |
| Table Turnover Report     | Average table occupancy time; turns per shift            | Daily         | Manager      |
| Void & Refund Report      | All voided orders with reason and approving manager      | Daily         | Manager      |
| Cashier Till Report       | Cash in, expected, variance per cashier                  | Daily         | Manager      |
| Inventory Depletion       | Stock used today vs. opening stock                       | Daily         | Manager      |
| Waste Log Report          | Total waste value, breakdown by item                     | Weekly        | Manager      |

### 8.2 Financial & Compliance Reports

| Report Name               | Description                                              | Frequency     | User         |
|---------------------------|----------------------------------------------------------|---------------|--------------|
| VAT Summary Report        | Total VATable sales, VAT collected, VAT-exempt sales     | Monthly       | Accountant/Owner |
| Z-Report                  | End-of-day fiscal summary for KRA                        | Daily         | Manager/Cashier |
| M-Pesa Reconciliation     | All M-Pesa transactions with reference codes            | Daily         | Cashier/Manager |
| Monthly P&L Summary       | Revenue vs. COGS (from inventory) per month              | Monthly       | Owner        |

---

## 9. Futuristic Features (Phase 2 & Beyond)

### 9.1 AI-Powered Intelligence

| Feature                              | Description                                                                 | Phase |
|--------------------------------------|-----------------------------------------------------------------------------|-------|
| Waiter Upsell AI                     | After waiter selects an item, system shows: "Customers who ordered this also add..." based on real sales correlation data | Phase 2 |
| Predictive Inventory Restocking      | AI analyzes 90 days of sales data + upcoming calendar (events, weather) to predict ingredient needs for the next 7 days | Phase 2 |
| Menu Optimization Suggestions        | AI flags slow-moving items for manager review; recommends removal or repricing | Phase 3 |
| Demand Forecasting                   | Predicts covers and revenue for next day/week to help scheduling and prep    | Phase 3 |
| Anomaly Detection                    | Flags unusual void patterns, suspicious discounts, or revenue drops in real time | Phase 2 |

### 9.2 Customer Engagement

| Feature                              | Description                                                                 | Phase |
|--------------------------------------|-----------------------------------------------------------------------------|-------|
| WhatsApp Receipt Delivery            | After payment, customer receives digital receipt via WhatsApp API (preferred over SMS in Kenya) | Phase 2 |
| Loyalty Points System                | Points earned per KES spent; redeemable for discounts or free items. Customer identified by phone number at payment | Phase 2 |
| Loyalty Tier Levels                  | Bronze / Silver / Gold tiers with escalating benefits based on cumulative spend | Phase 3 |
| Birthday/Anniversary Offers          | System sends WhatsApp vouchers to loyalty members on special dates          | Phase 3 |

### 9.3 Operational Intelligence

| Feature                              | Description                                                                 | Phase |
|--------------------------------------|-----------------------------------------------------------------------------|-------|
| Real-time Manager Dashboard          | Mobile-optimized web dashboard: live sales, open tables, kitchen queue, top-selling items — viewable on any phone | Phase 2 |
| Multi-Branch Cloud Management        | Single login for owner to view consolidated reports across all branches     | Phase 2 |
| KDS with AI Prep Timing              | KDS displays AI-estimated preparation time per dish based on kitchen load and historical prep data | Phase 3 |
| Kitchen Load Balancing               | System automatically routes orders to stations with lower load when multiple kitchen stations exist | Phase 3 |

---

## 10. Non-Functional Requirements

### 10.1 Availability & Reliability

| Req ID  | Requirement                                                                           | Target        |
|---------|---------------------------------------------------------------------------------------|---------------|
| NFR-01  | **Offline Mode:** All core functions (order taking, payment processing, receipt printing) must work without internet | Full offline capability |
| NFR-02  | **Sync on Reconnect:** All offline transactions synced to cloud within 60 seconds of connectivity restoration | < 60 seconds |
| NFR-03  | Cloud backend uptime (for sync, dashboards, reports)                                   | 99.5% monthly |
| NFR-04  | System must support UPS (Uninterruptible Power Supply) connected hardware to survive power dips | Hardware spec |

### 10.2 Performance

| Req ID  | Requirement                                                                           | Target     |
|---------|---------------------------------------------------------------------------------------|------------|
| NFR-05  | Order screen load time (from table tap to menu visible)                               | < 1.5 seconds |
| NFR-06  | Order send to kitchen (from "Fire" tap to KDS display)                                | < 2 seconds |
| NFR-07  | Payment processing completion (M-Pesa confirmation to receipt print)                  | < 45 seconds |
| NFR-08  | Receipt print time                                                                     | < 5 seconds |

### 10.3 Security

| Req ID  | Requirement                                                                           | Priority  |
|---------|---------------------------------------------------------------------------------------|-----------|
| NFR-09  | Role-based access control (RBAC) — every action permission-controlled                | Must Have |
| NFR-10  | All data transmitted over HTTPS/TLS 1.3                                               | Must Have |
| NFR-11  | Payment card data never stored on device (PCI-DSS scope minimization)                 | Must Have |
| NFR-12  | Full audit log: every action (order, void, discount, login) logged with user and timestamp | Must Have |
| NFR-13  | Manager PIN required for: voids, refunds, discounts above 10%, end-of-day close       | Must Have |

### 10.4 Hardware Compatibility

| Req ID  | Requirement                                                                           | Priority  |
|---------|---------------------------------------------------------------------------------------|-----------|
| NFR-14  | Runs on Android 10+ tablets (7-inch minimum; 10-inch recommended for waiter tablets)  | Must Have |
| NFR-15  | Runs on Windows 10/11 touchscreen terminal (for fixed cashier station)                | Must Have |
| NFR-16  | Supports Bluetooth thermal receipt printer (80mm)                                     | Must Have |
| NFR-17  | Supports USB/Ethernet Kitchen Display System monitor                                  | Must Have |
| NFR-18  | Supports USB cash drawer                                                               | Must Have |
| NFR-19  | Supports Bluetooth card payment terminal                                               | Must Have |

### 10.5 Data & Backup

| Req ID  | Requirement                                                                           | Target     |
|---------|---------------------------------------------------------------------------------------|------------|
| NFR-20  | Local database backup: automatic backup every 4 hours to local storage                | 4-hour RPO |
| NFR-21  | Cloud backup: daily encrypted backup to cloud storage                                 | 24-hour RPO |
| NFR-22  | Data retention: all transaction data retained minimum 7 years (KRA requirement)       | 7 years    |
| NFR-23  | Database encryption at rest (AES-256)                                                 | Must Have  |

---

## 11. Tech Stack Recommendation

### 11.1 Frontend (Waiter & Cashier Tablet/Terminal)

| Layer         | Technology                 | Rationale                                                       |
|---------------|----------------------------|-----------------------------------------------------------------|
| UI Framework  | React Native               | Single codebase for Android tablet + Windows; fast touchscreen UI |
| State Mgmt    | Redux Toolkit + RTK Query  | Predictable state for complex order flows                       |
| Offline DB    | SQLite (via expo-sqlite)   | Reliable local storage for offline order and transaction data   |
| Sync Engine   | Custom sync worker with conflict resolution | Queue-based sync: local-first, cloud-sync-on-connect |

### 11.2 Kitchen Display System (KDS)

| Layer         | Technology                 | Rationale                                                       |
|---------------|----------------------------|-----------------------------------------------------------------|
| KDS App       | React.js (web app on smart display) | Runs in browser on any Android TV or smart monitor     |
| Real-time     | WebSockets (Socket.io)     | Sub-second order updates to kitchen without polling             |

### 11.3 Backend (Cloud)

| Layer             | Technology                 | Rationale                                                    |
|-------------------|----------------------------|--------------------------------------------------------------|
| API Server        | Node.js + Express / NestJS | Fast async I/O ideal for payment callbacks and real-time sync |
| Database          | PostgreSQL                 | ACID-compliant; excellent for financial transaction records   |
| Cache             | Redis                      | Session management; menu caching; real-time counters          |
| Message Queue     | RabbitMQ / AWS SQS         | Reliable offline sync queue processing                        |
| File Storage      | AWS S3 / Cloudflare R2     | Menu images, report files, backups                            |
| Hosting           | AWS or Azure (Africa East region) | Low latency to Kenya; data sovereignty options          |

### 11.4 Integrations

| Integration       | Technology / Service              | Notes                                              |
|-------------------|-----------------------------------|----------------------------------------------------|
| M-Pesa Payments   | Safaricom Daraja API v2.0         | STK Push + C2B; webhook callback endpoint required |
| KRA eTIMS         | KRA OSCU/VSCU REST API            | TIS certification required; sandbox at etims-sbx.kra.go.ke |
| Card Payments     | Pesapal / DPO Group / KCB Merchant | PCI-DSS compliant hosted payment terminal SDKs  |
| WhatsApp Receipts | WhatsApp Business API (Meta Cloud) | Requires WABA account; template message approval  |
| Push Notifications| Firebase Cloud Messaging (FCM)    | Manager alerts, low stock notifications            |

### 11.5 DevOps & Infrastructure

| Layer             | Technology                 | Notes                                                        |
|-------------------|----------------------------|--------------------------------------------------------------|
| CI/CD             | GitHub Actions             | Automated testing and deployment pipeline                    |
| Containerization  | Docker + Kubernetes         | Scalable backend; zero-downtime deployments                  |
| Monitoring        | Sentry (errors) + Datadog (APM) | Real-time error tracking and performance monitoring      |
| Analytics         | PostHog or Metabase         | Embedded BI for manager dashboards                           |

---

---

# PRD 2: HOTEL POS & ROOM ORDERING SYSTEM

---

## 1. Executive Summary

This document defines the requirements for a **hotel-wide Point of Sale (POS) and Room Ordering System** for a full-service Kenyan hotel offering restaurant dining, bar service, room service, conference facilities, and spa services. The system integrates tightly with the hotel's **Property Management System (PMS)** to enable seamless guest folio management, room charge posting, and consolidated billing at checkout.

Ordering is **waiter-operated throughout** — waitstaff enter all orders on tablets. Guests in rooms may browse a digital menu on an in-room tablet and submit a request, but this is an **order request that triggers a waiter to action** — it is not automated delivery. This model maintains service quality while offering guests digital convenience.

The system addresses Kenya-specific compliance: KRA eTIMS, 16% VAT, 2% Tourism Fund (TF) levy, and operates at hotel-grade reliability (99.9% uptime target — hotels never close).

**Target:** 12–18 month phased delivery
**Primary Users:** Restaurant Waiters, Room Service Waiters, Bar Staff, Front Desk, Hotel Manager, Owner
**Core Integrations:** PMS (Opera/Protel/Custom), KRA eTIMS API, M-Pesa Daraja API, KDS, In-Room Tablet System

---

## 2. Business Context

### 2.1 Hotel Profile

| Attribute              | Detail                                                            |
|------------------------|-------------------------------------------------------------------|
| Hotel Type             | Full-service hotel (3–5 star)                                     |
| Location               | Kenya (Nairobi, Mombasa, Safari properties, or resort)            |
| Rooms                  | 20–250 rooms                                                      |
| F&B Outlets            | Restaurant, Bar/Lounge, Room Service, Conference Banqueting        |
| Additional Services    | Spa, Gift Shop, Swimming Pool Bar                                  |
| Guests                 | Business travelers, tourists, conference delegates, leisure guests |
| Primary Payment        | Room charge (folio), M-Pesa, Card, Corporate billing              |

### 2.2 Hotel Revenue Centre Structure

Hotels operate across multiple revenue-generating departments. The POS system must track revenue distinctly per centre:

| Revenue Centre         | Description                                                       |
|------------------------|-------------------------------------------------------------------|
| Restaurant             | Main dining outlet — breakfast, lunch, dinner                     |
| Bar / Lounge           | Alcoholic and non-alcoholic beverages; cocktail menu              |
| Room Service           | In-room food and beverage delivery 24/7                           |
| Minibar                | Per-room minibar consumption tracking                             |
| Conference & Banquet   | Group event catering; billed to event master account              |
| Spa & Wellness         | Treatments, products (if spa integrated)                          |
| Pool Bar               | Outdoor beverage and snack service                                |

### 2.3 Ordering Model & Guest Touchpoints

```
GUEST JOURNEY - ORDERING FLOW

In Restaurant/Bar:
Guest seated → Waiter approaches → Waiter takes verbal order →
Waiter enters on POS tablet → Order sent to KDS → Prepared →
Waiter delivers → Guest pays or charges to room

Room Service:
Guest browses in-room tablet menu → Submits ORDER REQUEST →
Room Service Waiter receives alert on tablet → Waiter confirms,
prepares in kitchen (KDS) → Delivers to room →
Bill posted to room folio automatically

Conference/Event:
Event planner creates Event Account → Delegates order →
Waiter enters orders tagged to Event Account →
End of event: consolidated bill generated → Corporate payment
```

---

## 3. User Personas

### Persona 1: Restaurant Waiter

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Name           | Fatuma, 26                                                             |
| Role           | Restaurant/Pool Waiter                                                 |
| Tech Comfort   | Moderate                                                               |
| Goal           | Fast order entry; charge to room without errors; upsell beverages      |
| Key Need       | Room number lookup; guest name auto-fill; quick "charge to room" flow  |

### Persona 2: Room Service Waiter

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Name           | Kevin, 28                                                              |
| Role           | Room Service Operator and Delivery Waiter                              |
| Tech Comfort   | Moderate                                                               |
| Goal           | Receive in-room requests instantly; create order quickly; track delivery |
| Key Need       | Room request alert; order creation by room number; delivery timer      |

### Persona 3: Bar Staff / Bartender

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Name           | Naomi, 30                                                              |
| Role           | Head Bartender                                                         |
| Tech Comfort   | Moderate-high                                                          |
| Goal           | Fast tab management; room charge posting; accurate stock tracking      |
| Key Need       | Open tab per guest; quick modifiers for cocktails; bar-specific KDS    |

### Persona 4: Front Desk / Receptionist

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Name           | Carol, 32                                                              |
| Role           | Front Desk Agent                                                       |
| Tech Comfort   | High                                                                   |
| Goal           | See accurate guest folio at all times; process checkout quickly        |
| Key Need       | Live folio view per room; outstanding F&B charges visible at checkout  |

### Persona 5: Hotel Manager / F&B Manager

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Name           | James, 42                                                              |
| Role           | F&B Manager                                                            |
| Tech Comfort   | High                                                                   |
| Goal           | Revenue per outlet; staff performance; compliance; cost control        |
| Key Need       | Real-time revenue dashboard; departmental P&L; void audit trail        |

### Persona 6: Guest (In-Room Tablet User)

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Name           | Sophie, 38 (business traveler from UK)                                 |
| Role           | Hotel Guest                                                            |
| Tech Comfort   | High                                                                   |
| Goal           | Order room service without calling reception; see charges clearly      |
| Key Need       | Intuitive menu; easy request submission; confirmation message          |

---

## 4. Hotel-Specific Functional Requirements

### 4.1 Room Service Ordering (Waiter-Operated)

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| RS-01    | Room service waiter creates new order by entering room number                          | Must Have |
| RS-02    | System validates room number: confirms room is occupied; displays guest name and check-in date | Must Have |
| RS-03    | Credit limit check: system queries PMS for room's charge authorization limit           | Must Have |
| RS-04    | Order tagged to room number and guest name; visible on KDS as "Room [number]"          | Must Have |
| RS-05    | Room service orders routed to Room Service KDS in kitchen (separate from restaurant KDS) | Must Have |
| RS-06    | Delivery timer: waiter marks "Out for Delivery"; system logs departure and delivery times | Must Have |
| RS-07    | Room service order automatically posted to guest folio in PMS on completion            | Must Have |
| RS-08    | Room service available 24/7; overnight orders supported                                | Must Have |
| RS-09    | Room service delivery charge automatically added to order where applicable             | Should Have |
| RS-10    | Waiter can call room from POS to confirm order details (Click-to-call integration)     | Nice to Have |

### 4.2 In-Room Tablet: Guest Request Interface

**IMPORTANT:** The in-room tablet is a **guest-facing menu browser and request submission tool.** The guest cannot self-complete an order. Every request creates an alert to a room service waiter who then processes and fulfills it.

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| IRT-01   | In-room tablet displays hotel F&B menu: Room Service menu, breakfast, all-day dining  | Must Have |
| IRT-02   | Guest can browse menu by category with images, descriptions, and prices                | Must Have |
| IRT-03   | Guest selects items and submits a REQUEST (not a confirmed order)                     | Must Have |
| IRT-04   | Submission sends instant alert to Room Service waiter tablet                           | Must Have |
| IRT-05   | Waiter reviews request, accepts, and converts to formal order in POS                  | Must Have |
| IRT-06   | Guest receives in-tablet confirmation: "Your order has been received. Estimated delivery: 25 min" | Must Have |
| IRT-07   | Tablet also displays: hotel information, spa menu, activities, local weather           | Should Have |
| IRT-08   | AI concierge suggestions on in-room tablet: "Good morning, would you like to see our breakfast menu?" | Nice to Have |
| IRT-09   | Voice ordering via in-room tablet microphone: guest speaks order; AI transcribes to request form | Nice to Have |
| IRT-10   | Guest can view their current room charges (folio view) on the in-room tablet           | Should Have |
| IRT-11   | In-room tablet app is kiosk-locked (cannot be used for general internet browsing)     | Must Have |
| IRT-12   | Tablet auto-wipes and resets on room checkout (GDPR-aligned data clearing)            | Must Have |

### 4.3 Bar & Lounge Operations

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| BAR-01   | Bar operates as a named outlet within the POS; revenue tracked separately             | Must Have |
| BAR-02   | Open tab per guest or per table (tab can run across multiple rounds)                   | Must Have |
| BAR-03   | Guest tab identified by room number (hotel guest) or by name/descriptor (walk-in)     | Must Have |
| BAR-04   | Bar-specific KDS or display screen showing drinks orders                               | Must Have |
| BAR-05   | Age verification flag on alcohol items (bartender must confirm before order accepted) | Should Have |
| BAR-06   | Happy hour pricing: time-based automated price reduction on selected items             | Should Have |
| BAR-07   | Bar inventory: bottle tracking, spirit measures, wastage logging                       | Must Have |

### 4.4 Conference & Event Billing

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| CONF-01  | Create event/conference account with event name, date, organizer contact, and authorized spend limit | Must Have |
| CONF-02  | Waiter assigns orders to event account instead of individual guest room               | Must Have |
| CONF-03  | Per-person package billing: conference package price x number of delegates            | Must Have |
| CONF-04  | Break service tracking: morning tea, lunch, afternoon tea logged per conference        | Must Have |
| CONF-05  | Event account consolidated invoice generated at event end                             | Must Have |
| CONF-06  | Corporate invoice generation with company name, VAT number, LPO reference             | Must Have |
| CONF-07  | AV services and equipment rental can be added to event account                        | Should Have |

### 4.5 Guest Folio Management

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| FOLIO-01 | Every guest room has a live running folio visible to front desk in real time           | Must Have |
| FOLIO-02 | F&B charges posted to folio automatically within 60 seconds of order completion       | Must Have |
| FOLIO-03 | Folio line items show: date/time, outlet, items consumed, amount, posting staff name  | Must Have |
| FOLIO-04 | Front desk can view folio from PMS or from POS (synced data)                          | Must Have |
| FOLIO-05 | Disputed charge: front desk can query charge from folio; POS shows original order     | Must Have |
| FOLIO-06 | Folio settlement at checkout: balance transferred to final bill in PMS                | Must Have |
| FOLIO-07 | Split folio: guest can request F&B charges on separate folio from room charges        | Should Have |
| FOLIO-08 | Credit limit management: alert when guest's F&B charges approach authorization limit  | Must Have |
| FOLIO-09 | Folio history: all posting history retained; no deletions; corrections via reversal only | Must Have |

### 4.6 Minibar Management

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| MINI-01  | Minibar item list configured per room type                                             | Must Have |
| MINI-02  | Housekeeping staff logs minibar consumption on tablet after room servicing             | Must Have |
| MINI-03  | Logged consumption automatically posted to guest folio                                | Must Have |
| MINI-04  | Minibar replenishment report generated for stock room                                  | Must Have |
| MINI-05  | IoT smart minibar integration: RFID/weight sensors auto-detect item removal and post to folio | Nice to Have |
| MINI-06  | Guest can view minibar charges on in-room tablet                                       | Should Have |

---

## 5. PMS Integration

### 5.1 Integration Architecture

The POS communicates with the hotel's PMS (Property Management System) via a standardized hotel technology interface. The POS must support integration with common PMS platforms used in Kenya: **Oracle OPERA**, **Protel**, **Hotelogix**, **Mews**, or a custom-built PMS.

```
POS System  <---> PMS Interface Layer (REST API / HTNG Protocol)  <---> PMS Database
                         |
                    Sync Events:
                    - Room check-in/checkout
                    - Guest name lookup
                    - Charge posting
                    - Credit limit check
                    - Folio balance query
```

### 5.2 PMS Integration Requirements

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| PMS-01   | Bi-directional integration: POS reads guest data from PMS; POS posts charges to PMS  | Must Have |
| PMS-02   | Room status sync: POS shows occupied/vacant status from PMS (updates every 5 min or via webhook) | Must Have |
| PMS-03   | Guest name auto-fill: when waiter enters room number, guest surname displayed immediately | Must Have |
| PMS-04   | Credit authorization: POS queries PMS credit limit before allowing room charge        | Must Have |
| PMS-05   | Charge posting: F&B charge posted to PMS folio with outlet code, amount, description, and timestamp | Must Have |
| PMS-06   | Checkout alert: PMS notifies POS when a guest checks out; prevents further room charges to that room | Must Have |
| PMS-07   | Rate plan access: POS can display guest's rate plan to identify package inclusions (e.g., breakfast included) | Should Have |
| PMS-08   | Support HTNG (Hotel Technology Next Generation) interface protocol                     | Should Have |
| PMS-09   | Support Oracle OPERA FIAS (Fiscal Interface Application Specification) for direct Opera integration | Should Have |
| PMS-10   | Fallback mode: if PMS is unreachable, POS works in standalone mode; sync charges when connection restored | Must Have |

---

## 6. Kenya Hospitality Compliance

### 6.1 KRA eTIMS Compliance

Same requirements as PRD 1 (TAX-01 through TAX-08) apply. Hotels have additional considerations:

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| HTAX-01  | Each hotel outlet (Restaurant, Bar, Room Service, Conference) registered as a separate revenue stream in eTIMS | Must Have |
| HTAX-02  | Consolidated fiscal receipt at guest checkout covers all F&B charges across all outlets | Must Have |
| HTAX-03  | eTIMS invoice generated per transaction at each outlet; folio bill generates a consolidated summary invoice | Must Have |

### 6.2 VAT on Hospitality Services

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| HVAT-01  | 16% VAT applied to all F&B sales, room service charges, minibar items                | Must Have |
| HVAT-02  | VAT breakdown visible on every receipt and every folio line item                      | Must Have |
| HVAT-03  | Conference packages: VAT applied to food and beverage components; services itemized separately | Must Have |

### 6.3 Tourism Fund (TF) Levy

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| TF-01    | 2% Tourism Fund levy auto-calculated on gross F&B sales (excluding VAT)               | Must Have |
| TF-02    | TF levy applicable to hotels meeting threshold: accommodation AND restaurants with gross sales > KES 3M/year | Must Have |
| TF-03    | Monthly TF levy report generated for submission to Tourism Fund eLevy portal by 10th of following month | Must Have |
| TF-04    | TF levy calculation: on gross sales EXCLUDING VAT and service charge                  | Must Have |
| TF-05    | TF levy tracked per outlet and consolidated for whole property                        | Must Have |

### 6.4 Service Charge & Other Levies

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| SC-01    | Optional service charge (e.g., 10%): configurable per outlet; excluded from TF levy calculation | Must Have |
| SC-02    | Service charge distribution report: how much distributed per waiter (tips management) | Should Have |

---

## 7. Payment Methods

| Req ID   | Requirement                                                                           | Priority |
|----------|---------------------------------------------------------------------------------------|----------|
| HPAY-01  | Room Charge: post to guest folio; requires PMS authorization; guest signs on tablet   | Must Have |
| HPAY-02  | M-Pesa (STK Push): as per PRD 1 M-Pesa requirements                                  | Must Have |
| HPAY-03  | Card Payment: Visa, Mastercard, Amex via PCI-DSS compliant terminal                   | Must Have |
| HPAY-04  | Cash: with change calculation and till management as per PRD 1                        | Must Have |
| HPAY-05  | Corporate / Company Account: bill to pre-approved company account; requires LPO or authorization letter | Must Have |
| HPAY-06  | Event/Conference Account: charges against pre-approved event budget                   | Must Have |
| HPAY-07  | Foreign Currency: USD, GBP, EUR accepted at front desk; converted at daily rate       | Should Have |
| HPAY-08  | Complimentary (Comp) billing: manager-authorized with reason code and approval trail  | Must Have |
| HPAY-09  | Split payment: portion charged to room, balance paid by M-Pesa or card               | Must Have |

---

## 8. Reporting & Analytics

### 8.1 Revenue Reports

| Report Name                    | Description                                                     | Frequency    | User             |
|--------------------------------|-----------------------------------------------------------------|--------------|------------------|
| Revenue by Department          | Restaurant, Bar, Room Service, Conference, Spa revenue          | Daily/Monthly | GM/F&B Manager  |
| RevPAR F&B Contribution        | F&B revenue per available room (food + bev contribution to RevPAR) | Monthly   | Owner/GM         |
| Outlet Comparison Report       | Side-by-side revenue, covers, average check per outlet          | Weekly        | F&B Manager      |
| Room Service Performance       | Orders, revenue, average delivery time, return rate             | Daily         | F&B Manager      |
| Conference Revenue Report      | Revenue per event; yield per delegate                           | Per Event     | Sales Manager    |
| Guest Spending Patterns        | Average F&B spend per room night; by guest nationality           | Monthly       | GM/Marketing     |

### 8.2 Compliance Reports

| Report Name                    | Description                                                     | Frequency    | User             |
|--------------------------------|-----------------------------------------------------------------|--------------|------------------|
| VAT Report                     | F&B VAT collected per outlet; monthly VAT filing summary        | Monthly       | Accountant        |
| Tourism Fund Levy Report       | 2% levy on gross F&B sales per month                            | Monthly       | Accountant        |
| KRA Z-Report                   | End-of-day fiscal report per outlet                             | Daily         | F&B Manager       |
| Folio Posting Audit            | All charges posted to rooms; by staff; discrepancies flagged    | Daily         | F&B Manager       |

### 8.3 Staff Performance Reports

| Report Name                    | Description                                                     | Frequency    | User             |
|--------------------------------|-----------------------------------------------------------------|--------------|------------------|
| Sales by Waiter per Shift      | Revenue, covers, upsell rate per waiter                         | Daily         | F&B Manager      |
| Void & Comp Report             | All voids and complimentaries with manager approvals            | Daily         | GM               |
| Table/Room Turnaround          | Service delivery metrics per outlet                             | Weekly        | F&B Manager      |

---

## 9. Futuristic Features (Phase 2 & Beyond)

### 9.1 AI-Powered Guest Experience

| Feature                              | Description                                                                 | Phase |
|--------------------------------------|-----------------------------------------------------------------------------|-------|
| AI Concierge on In-Room Tablet       | Personalized suggestions based on guest profile, time of day, weather, and previous orders: "Good morning, here is our breakfast menu — your favorite, the Full English, is available today" | Phase 2 |
| Predictive Room Service              | AI analyzes check-in time, flight origin, and past stays to predict breakfast preference and pre-stage ingredients | Phase 3 |
| Smart Upsell for Waiters             | Restaurant POS suggests wine pairing, dessert, or premium upgrade based on current order and guest history | Phase 2 |
| Guest Preference Memory              | Returning guests' preferences (dietary, allergies, favorite items) stored and shown to waiter on seating | Phase 3 |

### 9.2 Voice & IoT Features

| Feature                              | Description                                                                 | Phase |
|--------------------------------------|-----------------------------------------------------------------------------|-------|
| Voice-Activated Room Ordering        | Guest says "I'd like to order breakfast" to in-room tablet/smart speaker; AI transcribes and presents menu for confirmation | Phase 3 |
| IoT Smart Minibar                    | RFID or weight sensors in minibar auto-detect item removal; charge posted to folio automatically without housekeeping intervention | Phase 3 |
| IoT Kitchen Sensors                  | Temperature and prep-time sensors in kitchen surfaces integrate with KDS to provide real-time cook status | Phase 3 |
| Smart Room Integration               | When guest activates "Do Not Disturb" on room panel, room service alerts are muted and rescheduled | Phase 2 |

### 9.3 Biometric & Recognition Features

| Feature                              | Description                                                                 | Phase |
|--------------------------------------|-----------------------------------------------------------------------------|-------|
| Facial Recognition at Restaurant     | Guest identified by camera at restaurant entrance; waiter tablet shows guest name, room, preferences, and outstanding charges automatically | Phase 3 |
| Biometric Waiter Login               | Fingerprint replaces PIN on waiter tablets for faster login and stronger accountability | Phase 2 |

### 9.4 Communication & Automation

| Feature                              | Description                                                                 | Phase |
|--------------------------------------|-----------------------------------------------------------------------------|-------|
| WhatsApp Order Confirmation          | Guest receives WhatsApp message when room service order is accepted and when it is dispatched for delivery | Phase 2 |
| WhatsApp Bill Delivery               | At checkout, final F&B folio sent to guest's WhatsApp for records           | Phase 2 |
| Real-time Kitchen Load Balancing     | If restaurant kitchen is at capacity, room service orders are routed to a secondary kitchen or prep station automatically | Phase 3 |
| Predictive Staffing Alerts           | AI predicts busy periods and notifies manager to schedule additional F&B staff 48 hours in advance | Phase 3 |

---

## 10. Non-Functional Requirements

### 10.1 Availability & Reliability

| Req ID  | Requirement                                                                           | Target           |
|---------|---------------------------------------------------------------------------------------|------------------|
| HNFR-01 | System uptime target: hotel operations are 24/7/365 with no acceptable downtime window | 99.9% uptime     |
| HNFR-02 | Redundant local server on-premises (hotel LAN) + cloud backup — not purely cloud-dependent | Dual-mode architecture |
| HNFR-03 | If internet fails: all POS operations continue on local LAN; charges queue for PMS sync | Full LAN offline capability |
| HNFR-04 | Automatic failover: if cloud unreachable, local server takes over transparently within 30 seconds | < 30s failover   |
| HNFR-05 | UPS-protected on-premises server hardware                                              | Hardware spec     |
| HNFR-06 | Hardware: enterprise-grade WiFi (WiFi 6) across all F&B outlets for tablet connectivity | Infrastructure spec |

### 10.2 Performance

| Req ID  | Requirement                                                                           | Target     |
|---------|---------------------------------------------------------------------------------------|------------|
| HNFR-07 | Room charge lookup (enter room number → guest name displayed)                         | < 1 second |
| HNFR-08 | Charge posting to PMS folio                                                            | < 10 seconds |
| HNFR-09 | In-room tablet menu load time                                                          | < 2 seconds |
| HNFR-10 | Order from in-room tablet to waiter alert                                              | < 5 seconds |
| HNFR-11 | PMS sync latency for folio charges                                                     | < 60 seconds real-time posting |

### 10.3 Security & Compliance

| Req ID  | Requirement                                                                           | Priority  |
|---------|---------------------------------------------------------------------------------------|-----------|
| HNFR-12 | PCI-DSS Level compliance for card payment processing                                  | Must Have |
| HNFR-13 | Guest personal data handled per Kenya Data Protection Act 2019 (DPA) and GDPR-aligned standards | Must Have |
| HNFR-14 | In-room tablet data wiped on checkout (no guest data persisted between stays)         | Must Have |
| HNFR-15 | All data transmitted on hotel network over TLS 1.3; LAN traffic on isolated VLAN     | Must Have |
| HNFR-16 | Role-based access: Front Desk cannot see other guests' order details; only their own assigned folios | Must Have |
| HNFR-17 | Full audit log: all folio postings, voids, reversals with staff ID and timestamp      | Must Have |
| HNFR-18 | No card data stored on any device (use tokenization via payment gateway)              | Must Have |

### 10.4 Hardware Compatibility

| Component                | Specification                                                      |
|--------------------------|---------------------------------------------------------------------|
| Waiter Tablets           | Android 10+ (10–12 inch); gorilla glass; IP-rated for spill resistance |
| Cashier/Desk Terminal    | Windows 10/11 touchscreen all-in-one; 15-inch minimum               |
| Front Desk Terminal      | Integrated with PMS workstation (Windows)                           |
| In-Room Tablet           | Android 10+ (8–10 inch); wall-mounted or bedside holder; kiosk mode |
| Kitchen Display System   | 21-inch commercial-grade Android display or smart monitor            |
| Receipt Printers         | 80mm thermal; Ethernet-connected (hotel LAN) per outlet              |
| Cash Drawer              | USB/RJ11 connected per cashier station                               |
| Card Terminal            | Countertop and wireless POS terminals per outlet                     |
| Network Infrastructure   | WiFi 6 (802.11ax) enterprise access points; Gigabit LAN backbone     |
| Local Server             | On-premises rack server (minimum: 16-core CPU, 64GB RAM, RAID storage) for LAN operations |

### 10.5 Data & Backup

| Req ID  | Requirement                                                                           | Target     |
|---------|---------------------------------------------------------------------------------------|------------|
| HNFR-19 | Local server: automatic database backup every 1 hour to NAS                           | 1-hour RPO |
| HNFR-20 | Cloud backup: encrypted nightly backup to cloud storage (AWS S3 or Azure Blob)        | 24-hour RPO |
| HNFR-21 | Transaction data retained for 7 years minimum (KRA requirement)                       | 7 years    |
| HNFR-22 | Guest personal data retained for duration of stay + 2 years (DPA compliance)         | DPA-aligned |
| HNFR-23 | Point-in-time recovery capability: restore to any point in last 30 days               | 30-day PITR |

---

## 11. Tech Stack Recommendation

### 11.1 Frontend (Waiter Tablets, Cashier Terminals)

| Layer             | Technology                        | Rationale                                                  |
|-------------------|-----------------------------------|------------------------------------------------------------|
| UI Framework      | React Native                      | Shared codebase for Android tablets and Windows terminals  |
| Offline DB        | SQLite + WatermelonDB             | Fast reactive offline-first database                       |
| Real-time Updates | WebSockets (Socket.io)            | Instant alerts (room service requests, KDS updates)        |
| State Management  | Redux Toolkit                     | Complex multi-outlet state (restaurant, bar, room service) |

### 11.2 In-Room Tablet Application

| Layer             | Technology                        | Rationale                                                  |
|-------------------|-----------------------------------|------------------------------------------------------------|
| App Framework     | React Native (Android kiosk mode) | Kiosk-locked; single-purpose app with auto-update          |
| Content           | Contentful CMS or custom CMS      | Hotel F&B team updates menus without developer             |
| AI Chat (Phase 3) | OpenAI GPT-4o or Anthropic Claude API | Powers AI concierge and voice order transcription      |

### 11.3 Kitchen Display System

| Layer             | Technology                        | Rationale                                                  |
|-------------------|-----------------------------------|------------------------------------------------------------|
| KDS App           | React.js web app                  | Runs in browser on commercial display; zero-install        |
| Real-time         | WebSockets                        | Sub-second order delivery to kitchen screens               |
| Routing           | Server-side station routing rules | Orders directed to correct kitchen station                 |

### 11.4 Backend (Cloud + Local Server)

| Layer             | Technology                        | Rationale                                                  |
|-------------------|-----------------------------------|------------------------------------------------------------|
| API Server        | Node.js + NestJS                  | TypeScript; dependency injection; microservices-ready      |
| Local Server      | Same NestJS app deployed on-prem  | Hotel LAN operations when internet unavailable             |
| Database          | PostgreSQL                        | ACID transactions; excellent for financial records         |
| Cache             | Redis                             | Session cache; folio cache; real-time pub/sub              |
| Message Queue     | RabbitMQ                          | Reliable async processing: charge postings, eTIMS submissions, notifications |
| File Storage      | AWS S3 / Cloudflare R2            | Menu images, report archives, receipts                     |
| Hosting           | AWS (af-south-1 Cape Town region or eu-west-1 with Kenya CDN) | Low latency; data sovereignty |

### 11.5 Integrations

| Integration          | Technology / Protocol             | Notes                                              |
|----------------------|-----------------------------------|----------------------------------------------------|
| PMS (Opera)          | Oracle OPERA FIAS / HTNG REST     | Room status, folio posting, credit check           |
| PMS (Protel)         | Protel HTTP API                   | Supported by Lightspeed and others                 |
| PMS (Hotelogix/Mews) | REST API                          | Cloud-native PMS REST integrations                 |
| M-Pesa               | Safaricom Daraja API v2.0         | STK Push; C2B; callback webhook                    |
| KRA eTIMS            | KRA OSCU/VSCU REST API            | Per-outlet eTIMS configuration                     |
| Card Payments        | DPO Group / Pesapal / Equity Bank | PCI-DSS compliant; hotel-grade terminals           |
| WhatsApp             | Meta WhatsApp Business API        | Order confirmations; folio delivery at checkout    |
| Voice AI (Phase 3)   | Anthropic Claude API / OpenAI     | In-room voice order transcription and AI concierge |
| IoT Minibar (Phase 3)| MQTT protocol over hotel LAN      | Smart minibar RFID/weight sensors                  |

### 11.6 DevOps & Infrastructure

| Layer             | Technology                        | Notes                                                         |
|-------------------|-----------------------------------|---------------------------------------------------------------|
| CI/CD             | GitHub Actions                    | Automated build, test, deploy pipeline                        |
| Containers        | Docker + Kubernetes               | Cloud deployments; auto-scaling for peak periods              |
| Local Server OS   | Ubuntu Server LTS                 | Stable; low overhead for on-prem hotel server                 |
| Monitoring        | Sentry + Grafana + Prometheus     | Error tracking; infrastructure monitoring; uptime alerts       |
| Alerting          | PagerDuty / OpsGenie              | On-call alerts for 99.9% uptime maintenance                   |
| BI/Analytics      | Metabase (self-hosted)            | Hotel management dashboards; embedded analytics               |

---

## Appendix A: Compliance Summary Table

| Regulation                   | Applicability             | Requirement                         | Monthly Deadline |
|------------------------------|---------------------------|-------------------------------------|------------------|
| KRA VAT (16%)                | All F&B sales             | Collect, report, remit via iTax     | 20th of next month |
| KRA eTIMS                    | All businesses            | Digital fiscal receipt per sale     | Real-time / ongoing |
| Tourism Fund Levy (2%)       | Hotels, restaurants > KES 3M/yr | 2% on gross sales excl. VAT   | 10th of next month |
| Kenya Data Protection Act    | All guest data            | Consent, retention limits, deletion | Ongoing            |
| PCI-DSS                      | Card payments             | No card data stored; tokenization   | Annual assessment  |

---

## Appendix B: Integration Architecture Diagram (Descriptive)

```
+------------------+       +-------------------+       +------------------+
|  WAITER TABLETS  |       |  IN-ROOM TABLETS  |       | CASHIER TERMINAL |
|  (React Native)  |       |  (RN Kiosk Mode)  |       |  (React Native)  |
+--------+---------+       +---------+---------+       +--------+---------+
         |                           |                           |
         +---------------------------+---------------------------+
                                     |
                              WiFi / Hotel LAN
                                     |
                    +----------------+----------------+
                    |                                 |
           +--------+--------+             +----------+---------+
           |  LOCAL SERVER   |             |  CLOUD BACKEND     |
           |  (On-Premises)  |<----------->|  (AWS / Azure)     |
           |  NestJS + PG    |   Sync      |  NestJS + PG       |
           +--------+--------+             +----------+---------+
                    |                                 |
         +----------+----------+           +----------+----------+
         |                     |           |                     |
   +-----+------+    +---------+--+  +-----+------+   +---------+---+
   |  KDS       |    |  RECEIPT   |  | KRA eTIMS  |   | M-Pesa      |
   |  SCREENS   |    |  PRINTERS  |  | API        |   | Daraja API  |
   +------------+    +------------+  +------------+   +-------------+
                                           |
                                    +------+-------+
                                    |   PMS        |
                                    | (Opera/      |
                                    |  Protel/etc) |
                                    +--------------+
```

---

## Appendix C: Phased Delivery Roadmap

### Cafe/Restaurant POS

| Phase   | Timeline    | Deliverables                                                              |
|---------|-------------|---------------------------------------------------------------------------|
| Phase 1 | Months 1-4  | Core order taking, table map, KDS, cash/M-Pesa/card payment, eTIMS integration, Z-report |
| Phase 2 | Months 5-8  | Inventory management, loyalty program, WhatsApp receipts, manager mobile dashboard, multi-branch cloud |
| Phase 3 | Months 9-12 | AI upselling, predictive inventory, advanced analytics, voice features     |

### Hotel POS

| Phase   | Timeline    | Deliverables                                                              |
|---------|-------------|---------------------------------------------------------------------------|
| Phase 1 | Months 1-5  | Restaurant/bar POS, room charge posting, PMS integration, in-room tablet (basic), eTIMS, Tourism Fund levy |
| Phase 2 | Months 6-10 | Room service ordering flow, minibar logging, conference billing, WhatsApp notifications, AI upsell |
| Phase 3 | Months 11-18 | Voice ordering, IoT minibar, facial recognition, AI concierge, predictive kitchen load balancing |

---

*End of Document*

*Version 1.0 | April 2026 | Prepared for Developer Team & Investors*
*All figures, levy rates, and compliance requirements verified against KRA, Tourism Fund, and Safaricom Daraja documentation as of Q1 2026.*
