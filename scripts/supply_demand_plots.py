import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def plot_supply_demand_curve_matplotlib(supplier_data, supplier_prices, consumer_volume, consumer_prices, bus_name, snapshot_idx, n, supplier_labels=None):
    """
    Matplotlib version - static plot for given snapshot
    
    Parameters:
    - supplier_data: DataFrame or list of DataFrames
    - supplier_labels: list of custom names (optional)
    """
    
    # Handle single or multiple supplier data
    if isinstance(supplier_data, pd.DataFrame):
        supplier_data = [supplier_data]
        supplier_labels = supplier_labels or ['Supply']
    else:
        supplier_labels = supplier_labels or [f'Supply {i+1}' for i in range(len(supplier_data))]
    
    # Create subplots
    fig, axes = plt.subplots(len(supplier_data), 1, figsize=(10, 5 * len(supplier_data)))
    if len(supplier_data) == 1:
        axes = [axes]
    
    # Demand curve (same for all)
    demand_at_bus = consumer_volume.iloc[snapshot_idx][consumer_volume.iloc[snapshot_idx] > 0]
    demand_prices_at_bus = consumer_prices.loc[n.snapshots[snapshot_idx], demand_at_bus.index]
    
    demand_curve = pd.DataFrame({
        'dispatch': demand_at_bus.values,
        'price': demand_prices_at_bus.values
    }, index=demand_at_bus.index)
    
    demand_curve = demand_curve[demand_curve['dispatch'] > 0].sort_values('price', ascending=False)
    
    # Plot each supplier data type
    for idx, (supply_df, label) in enumerate(zip(supplier_data, supplier_labels)):
        ax = axes[idx]
        
        # Supply curve
        supply_at_bus = supply_df.iloc[snapshot_idx][supply_df.iloc[snapshot_idx] > 0]
        supply_prices_at_bus = supplier_prices.loc[n.snapshots[snapshot_idx], supply_at_bus.index]
        
        supply_curve = pd.DataFrame({
            'dispatch': supply_at_bus.values,
            'price': supply_prices_at_bus.values
        }, index=supply_at_bus.index)
        
        supply_curve = supply_curve[supply_curve['dispatch'] > 0].sort_values('price')
        
        max_dispatch = max(supply_curve['dispatch'].sum() if len(supply_curve) > 0 else 0,
                          demand_curve['dispatch'].sum() if len(demand_curve) > 0 else 0)
        
        # Plot supply
        ax.step(
            np.cumsum([0] + supply_curve['dispatch'].tolist()),
            supply_curve['price'].iloc[:1].tolist() + supply_curve['price'].tolist(),
            where='pre', linewidth=2, color='steelblue', label='Supply'
        )
        
        # Plot demand
        if len(demand_curve) > 0:
            ax.step(
                np.cumsum([0] + demand_curve['dispatch'].tolist()),
                demand_curve['price'].iloc[:1].tolist() + demand_curve['price'].tolist(),
                where='pre', linewidth=2, color='coral', label='Demand'
            )
        
        ax.set_xlim(0, max_dispatch)
        ax.set_xlabel('Cumulative Dispatch (MW)')
        ax.set_ylabel('Price (ZAR/MWh)')
        ax.set_title(f'{label} - {bus_name} at {n.snapshots[snapshot_idx]} (Snapshot {snapshot_idx})')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plot_supply_demand_curve_plotly(supplier_data, supplier_prices, consumer_volume, consumer_prices, bus_name, snapshot_idx, n, supplier_labels=None):
    """
    Plotly version - static plot for given snapshot
    Returns fig object
    """
    
    # Handle single or multiple supplier data
    if isinstance(supplier_data, pd.DataFrame):
        supplier_data = [supplier_data]
        supplier_labels = supplier_labels or ['Supply']
    else:
        supplier_labels = supplier_labels or [f'Supply {i+1}' for i in range(len(supplier_data))]
    
    # Demand curve (same for all)
    demand_at_bus = consumer_volume.iloc[snapshot_idx][consumer_volume.iloc[snapshot_idx] > 0]
    demand_prices_at_bus = consumer_prices.loc[n.snapshots[snapshot_idx], demand_at_bus.index]
    
    demand_curve = pd.DataFrame({
        'dispatch': demand_at_bus.values,
        'price': demand_prices_at_bus.values
    }, index=demand_at_bus.index)
    
    demand_curve = demand_curve[demand_curve['dispatch'] > 0].sort_values('price', ascending=False)
    
    # Create subplots
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=len(supplier_data), cols=1,
        subplot_titles=supplier_labels,
        vertical_spacing=0.12
    )
    
    # Plot each supplier data type
    for row_idx, (supply_df, label) in enumerate(zip(supplier_data, supplier_labels)):
        row = row_idx + 1
        
        # Supply curve
        supply_at_bus = supply_df.iloc[snapshot_idx][supply_df.iloc[snapshot_idx] > 0]
        supply_prices_at_bus = supplier_prices.loc[n.snapshots[snapshot_idx], supply_at_bus.index]
        
        supply_curve = pd.DataFrame({
            'dispatch': supply_at_bus.values,
            'price': supply_prices_at_bus.values
        }, index=supply_at_bus.index)
        
        supply_curve = supply_curve[supply_curve['dispatch'] > 0].sort_values('price')
        
        # Supply trace
        if len(supply_curve) > 0:
            supply_x = [0] + supply_curve['dispatch'].cumsum().tolist()
            supply_y = supply_curve['price'].iloc[:1].tolist() + supply_curve['price'].tolist()
            
            fig.add_trace(
                go.Scatter(
                    x=supply_x, y=supply_y, mode='lines', name='Supply',
                    line=dict(color='steelblue', width=2, shape='hv'),
                    hovertemplate='<b>Supply</b><br>Cumulative: %{x:.0f} MW<br>Price: €%{y:.0f}/MWh<extra></extra>'
                ),
                row=row, col=1
            )
        
        # Demand trace
        if len(demand_curve) > 0:
            demand_x = [0] + demand_curve['dispatch'].cumsum().tolist()
            demand_y = demand_curve['price'].iloc[:1].tolist() + demand_curve['price'].tolist()
            
            fig.add_trace(
                go.Scatter(
                    x=demand_x, y=demand_y, mode='lines', name='Demand',
                    line=dict(color='coral', width=2, shape='hv'),
                    hovertemplate='<b>Demand</b><br>Cumulative: %{x:.0f} MW<br>Price: €%{y:.0f}/MWh<extra></extra>'
                ),
                row=row, col=1
            )
    
    fig.update_xaxes(title_text='Cumulative Dispatch (MW)', row=len(supplier_data), col=1)
    fig.update_yaxes(title_text='Price (ZAR/MWh)', col=1)
    
    fig.update_layout(
        title=f'Supply-Demand Curves - {bus_name} at {n.snapshots[snapshot_idx]} (Snapshot {snapshot_idx})',
        height=400 * len(supplier_data),
        hovermode='x unified'
    )
    
    return fig


def plot_supply_demand_curve_interactive(supplier_data, supplier_prices, consumer_volume, consumer_prices, bus_name, n, supplier_labels=None):
    """
    Interactive Plotly version - dropdown to select snapshot
    Shows all supplier_data types in same snapshot via dropdown
    Returns fig object
    """
    
    # Handle single or multiple supplier data
    if isinstance(supplier_data, pd.DataFrame):
        supplier_data = [supplier_data]
        supplier_labels = supplier_labels or ['Supply']
    else:
        supplier_labels = supplier_labels or [f'Supply {i+1}' for i in range(len(supplier_data))]
    
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=len(supplier_data), cols=1,
        subplot_titles=supplier_labels,
        vertical_spacing=0.12
    )
    
    # Generate curves for all snapshots
    for snapshot_idx in range(len(n.snapshots)):
        # Demand curve (same for all)
        demand_at_bus = consumer_volume.iloc[snapshot_idx][consumer_volume.iloc[snapshot_idx] > 0]
        demand_prices_at_bus = consumer_prices.loc[n.snapshots[snapshot_idx], demand_at_bus.index]
        
        demand_curve = pd.DataFrame({
            'dispatch': demand_at_bus.values,
            'price': demand_prices_at_bus.values
        }, index=demand_at_bus.index)
        
        demand_curve = demand_curve[demand_curve['dispatch'] > 0].sort_values('price', ascending=False)
        
        # Plot each supplier data type
        for row_idx, (supply_df, label) in enumerate(zip(supplier_data, supplier_labels)):
            row = row_idx + 1
            
            # Supply curve
            supply_at_bus = supply_df.iloc[snapshot_idx][supply_df.iloc[snapshot_idx] > 0]
            supply_prices_at_bus = supplier_prices.loc[n.snapshots[snapshot_idx], supply_at_bus.index]
            
            supply_curve = pd.DataFrame({
                'dispatch': supply_at_bus.values,
                'price': supply_prices_at_bus.values
            }, index=supply_at_bus.index)
            
            supply_curve = supply_curve[supply_curve['dispatch'] > 0].sort_values('price')
            
            # Supply trace
            if len(supply_curve) > 0:
                supply_x = [0] + supply_curve['dispatch'].cumsum().tolist()
                supply_y = supply_curve['price'].iloc[:1].tolist() + supply_curve['price'].tolist()
                
                fig.add_trace(
                    go.Scatter(
                        x=supply_x, y=supply_y, mode='lines', name='Supply',
                        line=dict(color='steelblue', width=2, shape='hv'),
                        hovertemplate='<b>Supply</b><br>Cumulative: %{x:.0f} MW<br>Price: €%{y:.0f}/MWh<extra></extra>',
                        visible=(snapshot_idx == 0)
                    ),
                    row=row, col=1
                )
            
            # Demand trace
            if len(demand_curve) > 0:
                demand_x = [0] + demand_curve['dispatch'].cumsum().tolist()
                demand_y = demand_curve['price'].iloc[:1].tolist() + demand_curve['price'].tolist()
                
                fig.add_trace(
                    go.Scatter(
                        x=demand_x, y=demand_y, mode='lines', name='Demand',
                        line=dict(color='coral', width=2, shape='hv'),
                        hovertemplate='<b>Demand</b><br>Cumulative: %{x:.0f} MW<br>Price: €%{y:.0f}/MWh<extra></extra>',
                        visible=(snapshot_idx == 0)
                    ),
                    row=row, col=1
                )
    
    # Create dropdown buttons
    buttons = []
    traces_per_snapshot = len(supplier_data) * 2  # Supply + Demand for each
    
    for snapshot_idx in range(len(n.snapshots)):
        visible = [False] * len(fig.data)
        
        # Make traces for this snapshot visible
        for i in range(traces_per_snapshot):
            visible[snapshot_idx * traces_per_snapshot + i] = True
        
        buttons.append(
            dict(
                label=f'{snapshot_idx}: {n.snapshots[snapshot_idx]}',
                method='update',
                args=[{'visible': visible},
                      {'title': f'Supply-Demand Curves - {bus_name} at {n.snapshots[snapshot_idx]} (Snapshot {snapshot_idx})'}]
            )
        )
    
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=buttons,
                direction='down',
                x=0.01,
                xanchor='left',
                y=1.15,
                yanchor='top'
            )
        ],
        title=f'Supply-Demand Curves - {bus_name} at {n.snapshots[0]} (Snapshot 0)',
        height=400 * len(supplier_data),
        hovermode='x unified'
    )
    
    fig.update_xaxes(title_text='Cumulative Dispatch (MW)', row=len(supplier_data), col=1)
    fig.update_yaxes(title_text='Price (ZAR/MWh)', col=1)
    
    return fig