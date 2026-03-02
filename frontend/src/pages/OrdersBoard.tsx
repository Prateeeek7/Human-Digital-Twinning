import React, { useState, useEffect, useCallback } from 'react';
import { getOrderItems, submitOrders } from '../services/api';
import './OrdersBoard.css';

// Debounce helper for search input
const useDebounce = (value: string, delay: number) => {
    const [debouncedValue, setDebouncedValue] = useState(value);
    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);
        return () => clearTimeout(handler);
    }, [value, delay]);
    return debouncedValue;
};

const OrdersBoard: React.FC = () => {
    const [activeTab, setActiveTab] = useState('sets');
    const [scratchpad, setScratchpad] = useState<any[]>([]);

    // Catalog State
    const [searchTerm, setSearchTerm] = useState('');
    const debouncedSearch = useDebounce(searchTerm, 300);
    const [catalogItems, setCatalogItems] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    // Fetch live catalog data whenever tab or debounced search changes
    useEffect(() => {
        const fetchCatalog = async () => {
            if (activeTab === 'consults') {
                setCatalogItems([]); // Not implemented yet
                return;
            }
            setLoading(true);
            try {
                const data = await getOrderItems(activeTab, debouncedSearch);
                setCatalogItems(data);
            } catch (err) {
                console.error("Failed to load catalog", err);
            } finally {
                setLoading(false);
            }
        };
        fetchCatalog();
    }, [activeTab, debouncedSearch]);


    const addToScratchpad = (item: any, prefix: string = '') => {
        // Prevent pure duplicates, though in a real system we'd allow different doses
        if (!scratchpad.find(s => s.id === item.id)) {
            setScratchpad([...scratchpad, { ...item, display_prefix: prefix }]);
        }
    };

    const handleSignOrders = async () => {
        try {
            await submitOrders('PT-001', 'DR-SMITH', scratchpad);
            alert("SUCCESS: ORDER TRANSMISSION COMPLETED.");
            setScratchpad([]);
        } catch (err) {
            alert("ERROR: FAILED TO TRANSMIT ORDERS.");
        }
    };

    return (
        <div className="orders-board">
            {/* Left Categories Pane */}
            <div className="ob-pane-left">
                <div className="pane-header">
                    <span>ORDER CATALOG</span>
                    <span className="pane-subheader">CPOE MODULE</span>
                </div>
                <button
                    className={`ob-category-btn ${activeTab === 'sets' ? 'active' : ''}`}
                    onClick={() => setActiveTab('sets')}
                >
                    Order Sets (Pathways)
                </button>
                <button
                    className={`ob-category-btn ${activeTab === 'meds' ? 'active' : ''}`}
                    onClick={() => setActiveTab('meds')}
                >
                    Medications
                </button>
                <button
                    className={`ob-category-btn ${activeTab === 'labs' ? 'active' : ''}`}
                    onClick={() => setActiveTab('labs')}
                >
                    Laboratory
                </button>
                <button
                    className={`ob-category-btn ${activeTab === 'imaging' ? 'active' : ''}`}
                    onClick={() => setActiveTab('imaging')}
                >
                    Imaging & Diagnostics
                </button>
                <button
                    className={`ob-category-btn ${activeTab === 'consults' ? 'active' : ''}`}
                    onClick={() => setActiveTab('consults')}
                >
                    Consults
                </button>
            </div>

            {/* Main Ordering Area */}
            <div className="ob-pane-main">
                <div className="ob-form-section">
                    <h3>SEARCH & SELECT</h3>
                    <input
                        type="text"
                        className="ob-search"
                        placeholder={activeTab === 'meds' ? "Search 250,000+ Indian medications by brand or chemical composition..." : "Search catalog..."}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />

                    <div className="ob-list">
                        {loading ? (
                            <div style={{ padding: '1rem', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-family-mono)' }}>[ LOADING CATALOG DATA... ]</div>
                        ) : catalogItems.length === 0 ? (
                            <div style={{ padding: '1rem', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-family-mono)' }}>No results found.</div>
                        ) : (
                            <>
                                {debouncedSearch.trim() === '' && catalogItems.length > 6 && (
                                    <div style={{ padding: '0.75rem 1rem', color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-xs)', fontStyle: 'italic', borderBottom: '1px solid var(--color-border-subtle)' }}>
                                        Showing top 6 default options. Use search to browse the full catalog.
                                    </div>
                                )}
                                {(debouncedSearch.trim() === '' ? catalogItems.slice(0, 6) : catalogItems).map(item => (
                                    <div className="ob-order-item" key={item.id}>
                                        <div className="ob-item-details">
                                            <span className="ob-item-name">{item.name}</span>
                                            <span className="ob-item-dose" style={{ whiteSpace: 'pre-line' }}>{item.description}
                                                {item.details?.price_inr && ` | ₹${item.details.price_inr}`}
                                                {item.details?.manufacturer && ` | ${item.details.manufacturer}`}
                                            </span>
                                        </div>
                                        <button className="ob-add-btn" onClick={() => {
                                            if (item.type === 'set') {
                                                // Expand set components
                                                item.details.components.forEach((c: any) => {
                                                    addToScratchpad(c, `[${item.name}] `);
                                                });
                                            } else {
                                                addToScratchpad(item);
                                            }
                                        }}>
                                            {item.type === 'set' ? '+ APPLY PATHWAY' : '+ ADD'}
                                        </button>
                                    </div>
                                ))}
                            </>
                        )}
                    </div>
                </div>

                <div className="ob-scratchpad">
                    <div className="ob-sp-header">
                        <span className="ob-sp-title">DRAFT ORDERS (SCRATCHPAD)</span>
                        <button
                            className="ob-sign-btn"
                            disabled={scratchpad.length === 0}
                            onClick={handleSignOrders}
                        >
                            SIGN & SUBMIT
                        </button>
                    </div>

                    {scratchpad.length === 0 ? (
                        <div className="ob-empty-sp">No active orders in scratchpad.</div>
                    ) : (
                        <div className="ob-list">
                            {scratchpad.map((sItem, idx) => (
                                <div className="ob-order-item" style={{ backgroundColor: 'var(--color-bg-surface)' }} key={idx}>
                                    <span className="ob-item-name" style={{ fontFamily: 'var(--font-family-mono)', fontSize: '11px' }}>
                                        {sItem.display_prefix ? <span style={{ color: 'var(--color-text-secondary)' }}>{sItem.display_prefix}<br /></span> : null}
                                        {sItem.name} {sItem.type === 'med' ? '(Dose pending...)' : ''}
                                    </span>
                                    <button className="ob-add-btn" style={{ borderColor: 'var(--color-accent-red)', color: 'var(--color-accent-red)' }} onClick={() => {
                                        setScratchpad(scratchpad.filter((_, i) => i !== idx));
                                    }}>x REMOVE</button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default OrdersBoard;
