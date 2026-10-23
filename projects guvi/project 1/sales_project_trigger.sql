-- =======================================================================
-- Project: Sales Intelligence Hub (Branch-Based Sales Management System)
-- Deliverable: Database Trigger Implementation
-- File: sales_project_trigger.sql
-- =======================================================================

USE sales_management_db;

DELIMITER //

-- Drop existing triggers to avoid conflicts
DROP TRIGGER IF EXISTS trg_payment_splits_after_insert //
DROP TRIGGER IF EXISTS trg_payment_splits_after_update //
DROP TRIGGER IF EXISTS trg_payment_splits_after_delete //
DROP TRIGGER IF EXISTS update_received_amount //

-- Trigger 1: AFTER INSERT on payment_splits
-- Automatically calculates total amount paid, updates received_amount in customer_sales,
-- and updates status to 'Close' if payment is fully completed.
CREATE TRIGGER trg_payment_splits_after_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE v_total_paid DECIMAL(12,2);
    
    -- Calculate total payment received for this sale
    SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_paid
    FROM payment_splits
    WHERE sale_id = NEW.sale_id;
    
    -- Update received_amount and dynamically adjust status
    UPDATE customer_sales
    SET received_amount = v_total_paid,
        status = CASE 
            WHEN gross_sales <= v_total_paid THEN 'Close'
            ELSE 'Open'
        END
    WHERE sale_id = NEW.sale_id;
END //

-- Trigger 2: AFTER UPDATE on payment_splits
-- Ensures consistency if payment split amounts or sale references are modified
CREATE TRIGGER trg_payment_splits_after_update
AFTER UPDATE ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE v_total_new DECIMAL(12,2);
    DECLARE v_total_old DECIMAL(12,2);
    
    -- Update for new sale_id
    SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_new
    FROM payment_splits
    WHERE sale_id = NEW.sale_id;
    
    UPDATE customer_sales
    SET received_amount = v_total_new,
        status = CASE 
            WHEN gross_sales <= v_total_new THEN 'Close'
            ELSE 'Open'
        END
    WHERE sale_id = NEW.sale_id;
    
    -- If sale_id was changed, also recalculate for old sale_id
    IF OLD.sale_id <> NEW.sale_id THEN
        SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_old
        FROM payment_splits
        WHERE sale_id = OLD.sale_id;
        
        UPDATE customer_sales
        SET received_amount = v_total_old,
            status = CASE 
                WHEN gross_sales <= v_total_old THEN 'Close'
                ELSE 'Open'
            END
        WHERE sale_id = OLD.sale_id;
    END IF;
END //

-- Trigger 3: AFTER DELETE on payment_splits
-- Ensures received_amount adjusts automatically if a payment entry is removed
CREATE TRIGGER trg_payment_splits_after_delete
AFTER DELETE ON payment_splits
FOR EACH ROW
BEGIN
    DECLARE v_total_paid DECIMAL(12,2);
    
    SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_paid
    FROM payment_splits
    WHERE sale_id = OLD.sale_id;
    
    UPDATE customer_sales
    SET received_amount = v_total_paid,
        status = CASE 
            WHEN gross_sales <= v_total_paid THEN 'Close'
            ELSE 'Open'
        END
    WHERE sale_id = OLD.sale_id;
END //

DELIMITER ;
