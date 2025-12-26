import streamlit as st

# --- Helper Functions (Logic) ---
# Note: Corrected '10e6' (10 million) to '1e6' (1 million) for standard conversions
# and '10e3' to '1e3'.

def mgml_to_mM(mgml, kDa):
    if kDa == 0: return 0
    return mgml / kDa

def mM_to_nM(mM):
    return mM * 1e6 

def nM_to_mM(nM):
    return nM / 1e6

def nM_to_ugml(nM, kDa):
    # derived: nM * (g/mol / 1000) -> ug/mL logic specific to your workflow
    return nM * kDa / 1e3 

def mL_to_uL(mL):
    return mL * 1000

def uL_to_mL(uL):
    return uL / 1000

def find_total_volume(number_of_wells, volume_per_well):
    return number_of_wells * volume_per_well

def total_num_cells(cells_per_mL, total_volume_cells):
    return cells_per_mL * total_volume_cells

def num_of_cells_needed(cells_per_well, num_of_wells):
    return cells_per_well * num_of_wells

def volume_cells_from_total_volume_of_cells(initial_num_cells_per_mL, cells_per_well, num_of_wells):
    if initial_num_cells_per_mL == 0: return 0
    return num_of_cells_needed(cells_per_well, num_of_wells) / initial_num_cells_per_mL

def resuspension_volume_uL(num_wells, vol_per_well_uL):
    return num_wells * vol_per_well_uL

def generate_csv(data_dict):
    """Converts a dictionary of data into a simple CSV string."""
    csv_string = "Name,Value\n"
    for name, value in data_dict.items():
        # Format floats to 4 decimal places for cleanliness, or string otherwise
        if isinstance(value, float):
            csv_string += f"{name},{value:.4f}\n"
        else:
            csv_string += f"{name},{value}\n"
    return csv_string

# --- Streamlit UI ---

st.set_page_config(page_title="BioLab Calculator", page_icon="🧪")

st.title("🧪 BioLab Experiment Calculator")
st.markdown("Select the tool you need from the sidebar to get started.")

# Sidebar for navigation
tool_mode = st.sidebar.selectbox(
    "Select Calculator Mode",
    ["Cell Count Calculator", "Drug Dilution Calculator", "Stock Volume Calculator", "Unit Converters"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Experiment Helper v1.0")

# --- Mode 1: Cell Count Calculator ---
if tool_mode == "Cell Count Calculator":
    st.header("🧫 Cell Count & Volume Calculator")
    st.markdown("Calculate the volume of cell suspension needed for your plate.")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Stock Inputs")
        init_cells_per_ml = st.number_input("Initial Cells per mL", value=1.03e6, format="%.2e")
        init_vol_cells = st.number_input("Initial Volume of Cells (mL)", value=16.0)

    with col2:
        st.subheader("Plate Inputs")
        cells_per_well = st.number_input("Target Cells per Well", value=25000)
        num_wells = st.number_input("Number of Wells", value=30)
        vol_per_well_ul = st.number_input("Volume per Well (µL)", value=50.0)

    # Calculations
    vol_per_well_ml = uL_to_mL(vol_per_well_ul)
    
    total_cells = total_num_cells(init_cells_per_ml, init_vol_cells)
    cells_needed = num_of_cells_needed(cells_per_well, num_wells)
    
    # Calculate volume of cells needed (mL)
    vol_cells_needed_ml = volume_cells_from_total_volume_of_cells(init_cells_per_ml, cells_per_well, num_wells)
    vol_cells_needed_ul = mL_to_uL(vol_cells_needed_ml)
    
    # Calculate Total Volume required for the wells
    total_vol_required_ml = find_total_volume(num_wells, vol_per_well_ml)
    
    # Calculate resuspension volume (mL)
    resuspension_vol_ml = resuspension_volume_uL(num_wells, vol_per_well_ul)

    st.markdown("---")
    st.subheader("Results")
    
    # Display metrics in columns
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Cells Available", f"{total_cells:.2e}")
    m2.metric("Cells Needed", f"{cells_needed:.2e}")
    
    # Metric 3: Stock Volume
    if vol_cells_needed_ml >= 1:
        val3, unit3 = f"{vol_cells_needed_ml:.2f}", "mL"
    else:
        val3, unit3 = f"{mL_to_uL(vol_cells_needed_ml):.2f}", "µL"
    m3.metric(f"Stock Vol Needed ({unit3})", f"{val3}")

    # Metric 4: Resuspension Volume
    if resuspension_vol_ml >= 1:
        val4, unit4 = f"{resuspension_vol_ml:.2f}", "mL"
    else:
        val4, unit4 = f"{mL_to_uL(resuspension_vol_ml):.1f}", "µL"
    m4.metric(f"Resuspension Vol ({unit4})", f"{val4}")
    
# Data Export
    export_data = {
        "Input: Initial Cells per mL": init_cells_per_ml,
        "Input: Initial Volume (mL)": init_vol_cells,
        "Input: Target Cells per Well": cells_per_well,
        "Input: Number of Wells": num_wells,
        "Input: Volume per Well (uL)": vol_per_well_ul,
        "Result: Total Cells Available": total_cells,
        "Result: Cells Needed": cells_needed,
        "Result: Stock Volume Needed (mL)": vol_cells_needed_ml,
        "Result: Stock Volume Needed (uL)": vol_cells_needed_ul
    }
    
    st.download_button(
        label="📥 Download Results as CSV",
        data=generate_csv(export_data),
        file_name="cell_count_results.csv",
        mime="text/csv"
    )
    
# --- Mode 2: Drug Dilution Calculator ---
elif tool_mode == "Drug Dilution Calculator":
    st.header("💊 Drug Dilution Calculator")
    st.markdown("Calculate volumes for drug dilution based on intermediate concentration.")

    col1, col2 = st.columns(2)
    
    with col1:
        init_conc_nm = st.number_input("Initial Concentration (nM)", value=47933.33)
        final_conc_nm = st.number_input("Final Concentration (nM)", value=400.0)
    
    with col2:
        multiply_factor = st.number_input("Multiply Factor", value=1.0)
        num_wells = st.number_input("Number of Wells", value=18, step=1)
        vol_per_well_ul = st.number_input("Volume per Well (µL)", value=50.0)

    # Calculations
    volume_required = num_wells * vol_per_well_ul
    intermediate_conc = final_conc_nm * multiply_factor
    
    if intermediate_conc > 0:
        dilution_factor = init_conc_nm / intermediate_conc
        if dilution_factor > 0:
            volume_of_AB = volume_required / dilution_factor
            volume_of_media = volume_required - volume_of_AB
        else:
            volume_of_AB, volume_of_media = 0, 0
    else:
        dilution_factor, volume_of_AB, volume_of_media = 0, 0, 0

    st.markdown("---")
    st.subheader("Preparation Protocol")
    
    r1, r2, r3 = st.columns(3)
    r1.metric("Total Volume Required", f"{volume_required:.1f} µL")
    r2.metric("Dilution Factor", f"{dilution_factor:.2f}X")
    r3.metric("Intermediate Conc.", f"{intermediate_conc:.1f} nM")

    # Define a custom style for a large "Success" box
    st.markdown(
        f"""
        <div style="
            background-color: #c8a5d9;
            color: #000000;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #ffffff;
            font-size: 24px;
            line-height: 1.6;
        ">
            <strong>Mix:</strong><br>
            • <b>{volume_of_AB:.2f} µL</b> of Drug (Stock)<br>
            • <b>{volume_of_media:.2f} µL</b> of Media
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Data Export
    export_data = {
        "Input: Initial Conc (nM)": init_conc_nm,
        "Input: Final Conc (nM)": final_conc_nm,
        "Input: Multiply Factor": multiply_factor,
        "Input: Number of Wells": num_wells,
        "Input: Volume per Well (uL)": vol_per_well_ul,
        "Result: Total Volume Required (uL)": volume_required,
        "Result: Intermediate Conc (nM)": intermediate_conc,
        "Result: Dilution Factor": dilution_factor,
        "Result: Volume of Drug Stock (uL)": volume_of_AB,
        "Result: Volume of Media (uL)": volume_of_media
    }

    st.download_button(
        label="📥 Download Results as CSV",
        data=generate_csv(export_data),
        file_name="drug_dilution_results.csv",
        mime="text/csv"
    )


# --- Mode 3: Stock Volume Calculator ---
elif tool_mode == "Stock Volume Calculator":
    st.header("🧪 Stock vs Diluant Volume")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        num_wells = st.number_input("Number of Wells", value=25)
    with c2:
        vol_per_well_ul = st.number_input("Volume per Well (µL)", value=25.0)
    with c3:
        dilution = st.number_input("Dilution Factor", value=5.0)

    # Calculations
    total_volume_ul = find_total_volume(num_wells, vol_per_well_ul)
    
    if dilution > 0:
        stock = total_volume_ul / dilution
        diluant = total_volume_ul - stock
    else:
        stock, diluant = 0, 0

    st.markdown("---")
    st.metric("Total Volume Needed", f"{total_volume_ul:.1f} µL")
    
    st.table({
        "Component": ["Stock Solution", "Diluant", "Total"],
        "Volume (µL)": [f"{stock:.2f}", f"{diluant:.2f}", f"{total_volume_ul:.2f}"]
    })
    
    # Data Export
    export_data = {
        "Input: Number of Wells": num_wells,
        "Input: Volume per Well (uL)": vol_per_well_ul,
        "Input: Dilution Factor": dilution,
        "Result: Total Volume Needed (uL)": total_volume_ul,
        "Result: Volume of Stock (uL)": stock,
        "Result: Volume of Diluant (uL)": diluant
    }

    st.download_button(
        label="📥 Download Results as CSV",
        data=generate_csv(export_data),
        file_name="stock_volume_results.csv",
        mime="text/csv"
    )

# --- Mode 4: Quick Converters ---
elif tool_mode == "Unit Converters":
    st.header("🔄 Quick Unit Converters")
    
    st.subheader("Concentration: mM ↔ nM")
    c_val = st.number_input("Value", value=1.0)
    st.write(f"{c_val} mM = **{mM_to_nM(c_val):.2f} nM**")
    st.write(f"{c_val} nM = **{nM_to_mM(c_val):.6f} mM**")
    
    st.markdown("---")
    st.subheader("Mass/Molarity: nM ↔ µg/mL")
    col_a, col_b = st.columns(2)
    with col_a:
        nm_input = st.number_input("Concentration (nM)", value=100.0)
    with col_b:
        kda_input = st.number_input("Molecular Weight (kDa)", value=150.0)
        
    st.write(f"Result: **{nM_to_ugml(nm_input, kda_input):.4f} µg/mL**")