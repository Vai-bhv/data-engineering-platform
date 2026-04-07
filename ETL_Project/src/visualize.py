import os
import pandas as pd
import matplotlib.pyplot as plt

# Define directories for transformed data and output visualizations
TRANSFORMED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'transformed')
VISUAL_DIR = os.path.join(os.path.dirname(__file__), '..', 'visualizations')
os.makedirs(VISUAL_DIR, exist_ok=True)

def plot_program_distribution():
    # Load transformed akris data
    file_path = os.path.join(TRANSFORMED_DIR, "akris_transformed.csv")
    df = pd.read_csv(file_path)
    
    # Use normalized column name 'misto_konani'
    if 'misto_konani' in df.columns:
        distribution = df['misto_konani'].value_counts()
    else:
        distribution = pd.Series()
    
    plt.figure(figsize=(10,6))
    distribution.plot(kind='bar')
    plt.xlabel('Location')
    plt.ylabel('Number of Accredited Programs')
    plt.title('Program Distribution by Location')
    plt.tight_layout()
    output_file = os.path.join(VISUAL_DIR, 'program_distribution.png')
    plt.savefig(output_file)
    plt.close()
    print(f"Visualization saved: {output_file}")

def plot_social_service_statistics():
    # Load social service transformed data
    file_path = os.path.join(TRANSFORMED_DIR, "social_service_transformed.csv")
    df = pd.read_csv(file_path)
    
    # Group by municipality text ('obec_txt') and sum 'hodnota'
    if 'obec_txt' in df.columns and 'hodnota' in df.columns:
        stats = df.groupby('obec_txt')['hodnota'].sum().sort_values(ascending=False)
    else:
        stats = pd.Series()
    
    plt.figure(figsize=(10,6))
    stats.plot(kind='bar')
    plt.xlabel('Municipality')
    plt.ylabel('Total Facilities')
    plt.title('Social Service Facilities by Municipality')
    plt.tight_layout()
    output_file = os.path.join(VISUAL_DIR, 'social_service_statistics.png')
    plt.savefig(output_file)
    plt.close()
    print(f"Visualization saved: {output_file}")

def plot_rpss_distribution():
    # Load rpss transformed data
    file_path = os.path.join(TRANSFORMED_DIR, "rpss_transformed.csv")
    df = pd.read_csv(file_path)
    
    # Use 'kraj' as the region and 'kapacita' as the capacity field
    if 'kraj' in df.columns and 'kapacita' in df.columns:
        distribution = df.groupby('kraj')['kapacita'].mean().sort_values(ascending=False)
        ylabel = 'Average Capacity'
        title = 'RPSS Average Capacity by Region (kraj)'
    else:
        # Fallback: count records per region if available.
        if 'kraj' in df.columns:
            distribution = df['kraj'].value_counts()
            ylabel = 'Record Count'
            title = 'RPSS Record Count by Region (kraj)'
        else:
            distribution = pd.Series()
            ylabel = ''
            title = 'RPSS Distribution'
    
    plt.figure(figsize=(10,6))
    distribution.plot(kind='line', marker='o')
    plt.xlabel('Region (kraj)')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    output_file = os.path.join(VISUAL_DIR, 'rpss_distribution.png')
    plt.savefig(output_file)
    plt.close()
    print(f"Visualization saved: {output_file}")

def main():
    print("Generating visualizations...")
    plot_program_distribution()
    plot_social_service_statistics()
    plot_rpss_distribution()
    print("Visualizations complete.")

if __name__ == "__main__":
    main()
