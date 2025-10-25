# Hardware Detection & Model Recommendations

## Future Enhancement Proposal

Automatically detect system hardware and recommend optimal LLM models based on available resources.

---

## Overview

Instead of users manually selecting models, the system would:
1. Detect CPU, GPU, and RAM specifications
2. Recommend models that fit the hardware profile
3. Warn about models that may be too large
4. Suggest optimal configurations

---

## Hardware Detection Strategy

### **1. CPU Detection**

```python
import platform
import psutil

def detect_cpu():
    """Detect CPU specifications"""
    return {
        "processor": platform.processor(),
        "cores_physical": psutil.cpu_count(logical=False),
        "cores_logical": psutil.cpu_count(logical=True),
        "architecture": platform.machine(),  # x86_64, arm64, etc.
    }
```

### **2. GPU Detection**

```python
def detect_gpu():
    """Detect GPU specifications"""
    gpu_info = {
        "has_gpu": False,
        "gpu_type": None,
        "vram_gb": 0
    }
    
    # macOS - Metal
    if platform.system() == "Darwin":
        try:
            import subprocess
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True
            )
            if "Apple" in result.stdout:
                gpu_info["has_gpu"] = True
                gpu_info["gpu_type"] = "Apple Silicon"
                # Parse VRAM from output
        except Exception:
            pass
    
    # NVIDIA CUDA
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info["has_gpu"] = True
            gpu_info["gpu_type"] = "NVIDIA CUDA"
            gpu_info["vram_gb"] = torch.cuda.get_device_properties(0).total_memory / 1e9
    except ImportError:
        pass
    
    # AMD ROCm
    try:
        import torch
        if hasattr(torch, 'hip') and torch.hip.is_available():
            gpu_info["has_gpu"] = True
            gpu_info["gpu_type"] = "AMD ROCm"
    except (ImportError, AttributeError):
        pass
    
    return gpu_info
```

### **3. RAM Detection**

```python
def detect_ram():
    """Detect RAM specifications"""
    mem = psutil.virtual_memory()
    return {
        "total_gb": mem.total / 1e9,
        "available_gb": mem.available / 1e9,
        "percent_used": mem.percent
    }
```

---

## Model Recommendation Logic

### **Hardware Profiles**

```python
HARDWARE_PROFILES = {
    "minimal": {
        "ram_gb": 8,
        "recommended_models": ["phi3:mini", "tinyllama:1.1b"],
        "max_params": "3B",
        "description": "Basic systems with limited RAM"
    },
    "standard": {
        "ram_gb": 16,
        "recommended_models": ["llama3.1:8b", "mistral:7b", "qwen2.5:7b"],
        "max_params": "8B",
        "description": "Standard laptops and desktops"
    },
    "performance": {
        "ram_gb": 32,
        "recommended_models": ["llama3.1:13b", "mixtral:8x7b"],
        "max_params": "13B",
        "description": "High-end workstations"
    },
    "enthusiast": {
        "ram_gb": 64,
        "recommended_models": ["llama3.1:70b", "qwen2.5:32b"],
        "max_params": "70B",
        "description": "Professional workstations with ample resources"
    }
}
```

### **Recommendation Engine**

```python
def recommend_models(hardware_info):
    """Recommend models based on hardware"""
    ram_gb = hardware_info["ram"]["total_gb"]
    has_gpu = hardware_info["gpu"]["has_gpu"]
    gpu_type = hardware_info["gpu"]["gpu_type"]
    
    # Determine profile
    if ram_gb >= 64:
        profile = "enthusiast"
    elif ram_gb >= 32:
        profile = "performance"
    elif ram_gb >= 16:
        profile = "standard"
    else:
        profile = "minimal"
    
    recommendations = HARDWARE_PROFILES[profile].copy()
    
    # Adjust for GPU
    if has_gpu:
        if gpu_type == "Apple Silicon":
            # Apple Silicon can handle larger models efficiently
            recommendations["note"] = "Apple Silicon detected - excellent for LLMs"
            if profile == "performance":
                recommendations["recommended_models"].append("llama3.1:70b")
        elif gpu_type == "NVIDIA CUDA":
            vram = hardware_info["gpu"]["vram_gb"]
            if vram >= 24:
                recommendations["note"] = f"High VRAM ({vram:.0f}GB) - can handle large models"
            elif vram >= 12:
                recommendations["note"] = f"Good VRAM ({vram:.0f}GB) - suitable for 13B models"
            else:
                recommendations["note"] = f"Limited VRAM ({vram:.0f}GB) - stick to 7B models"
    else:
        recommendations["note"] = "CPU-only - performance may be slower"
    
    return recommendations
```

---

## UI Integration

### **Hardware Status Display**

```python
def render_hardware_status():
    """Display hardware information and recommendations"""
    
    st.subheader("💻 Hardware Profile")
    
    # Detect hardware
    hw_info = {
        "cpu": detect_cpu(),
        "gpu": detect_gpu(),
        "ram": detect_ram()
    }
    
    # Display specs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "CPU",
            f"{hw_info['cpu']['cores_physical']} cores",
            help=f"Architecture: {hw_info['cpu']['architecture']}"
        )
    
    with col2:
        if hw_info["gpu"]["has_gpu"]:
            gpu_label = hw_info["gpu"]["gpu_type"]
            if hw_info["gpu"]["vram_gb"] > 0:
                gpu_label += f" ({hw_info['gpu']['vram_gb']:.0f}GB)"
            st.metric("GPU", gpu_label)
        else:
            st.metric("GPU", "CPU Only")
    
    with col3:
        st.metric(
            "RAM",
            f"{hw_info['ram']['total_gb']:.0f}GB",
            delta=f"{hw_info['ram']['available_gb']:.0f}GB free"
        )
    
    # Get recommendations
    recommendations = recommend_models(hw_info)
    
    st.divider()
    
    # Display recommendations
    st.subheader("🎯 Recommended Models")
    st.caption(recommendations["description"])
    
    if "note" in recommendations:
        st.info(f"💡 {recommendations['note']}")
    
    # Show recommended models
    for model in recommendations["recommended_models"]:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"✨ **{model}**")
        with col2:
            if st.button(f"Pull", key=f"pull_{model}"):
                # Pull model logic
                pass
```

---

## Model Size Warnings

### **Automatic Warnings**

```python
def check_model_compatibility(model_name, hardware_info):
    """Check if model is compatible with hardware"""
    
    # Extract parameter count from model name
    param_match = re.search(r'(\d+)b', model_name.lower())
    if not param_match:
        return {"compatible": True, "warning": None}
    
    params_b = int(param_match.group(1))
    ram_gb = hardware_info["ram"]["total_gb"]
    
    # Rule of thumb: Need ~2GB RAM per 1B parameters
    required_ram = params_b * 2
    
    if required_ram > ram_gb * 0.8:  # Use 80% as threshold
        return {
            "compatible": False,
            "warning": f"⚠️ {model_name} requires ~{required_ram}GB RAM, but you have {ram_gb:.0f}GB. Performance may be poor."
        }
    elif required_ram > ram_gb * 0.6:
        return {
            "compatible": True,
            "warning": f"⚠️ {model_name} may use significant RAM (~{required_ram}GB). Monitor performance."
        }
    else:
        return {
            "compatible": True,
            "warning": None
        }
```

---

## Implementation Plan

### **Phase 1: Basic Detection**
- [ ] Implement CPU detection
- [ ] Implement RAM detection
- [ ] Create hardware profile display
- [ ] Add to LLM Health Controls

### **Phase 2: GPU Detection**
- [ ] Detect Apple Silicon
- [ ] Detect NVIDIA CUDA
- [ ] Detect AMD ROCm
- [ ] Display GPU info in UI

### **Phase 3: Recommendations**
- [ ] Create recommendation engine
- [ ] Define hardware profiles
- [ ] Show recommended models
- [ ] Add quick-pull buttons

### **Phase 4: Warnings**
- [ ] Implement compatibility checker
- [ ] Show warnings before pulling large models
- [ ] Add performance tips
- [ ] Monitor resource usage during generation

---

## Example UI Flow

### **Before (Current)**
```
⚙️ LLM Health & Controls
├─ System Status
├─ Ollama Controls
├─ Model Selection
└─ Model Management
    └─ User manually enters model name
```

### **After (With Hardware Detection)**
```
⚙️ LLM Health & Controls
├─ 💻 Hardware Profile
│   ├─ CPU: 10 cores (Apple M2)
│   ├─ GPU: Apple Silicon
│   └─ RAM: 64GB (58GB free)
│
├─ 🎯 Recommended Models (Enthusiast Profile)
│   ├─ ✨ llama3.1:70b [Pull]
│   ├─ ✨ qwen2.5:32b [Pull]
│   └─ ✨ mixtral:8x7b [Pull]
│
├─ System Status
├─ Ollama Controls
├─ Model Selection
└─ Model Management
    └─ Smart warnings when pulling incompatible models
```

---

## Benefits

### **For Users:**
1. ✅ **No guessing** - System recommends optimal models
2. ✅ **Avoid issues** - Warnings prevent pulling models that won't run
3. ✅ **Better performance** - Use models matched to hardware
4. ✅ **Quick setup** - One-click pull recommended models

### **For Developers:**
1. ✅ **Fewer support issues** - Users pick appropriate models
2. ✅ **Better UX** - Guided experience
3. ✅ **Performance insights** - Track hardware usage

---

## Dependencies

### **Required:**
```toml
[dependencies]
psutil = ">=5.9.0"  # Already included
```

### **Optional (for GPU detection):**
```toml
[optional-dependencies]
gpu = [
    "torch>=2.0.0",  # For CUDA/ROCm detection
    "py3nvml>=0.2.7",  # For NVIDIA GPU info
]
```

---

## Platform-Specific Notes

### **macOS**
- Use `system_profiler` for GPU info
- Apple Silicon detection via `platform.machine() == 'arm64'`
- Metal acceleration available by default

### **Linux**
- Use `lspci` or `nvidia-smi` for GPU
- Check `/proc/cpuinfo` for CPU details
- ROCm detection via torch

### **Windows**
- Use `wmic` for hardware info
- DirectML for GPU acceleration
- CUDA detection via torch

---

## Testing Strategy

### **Test Cases:**

1. **Minimal Hardware** (8GB RAM, no GPU)
   - Should recommend: phi3:mini, tinyllama
   - Should warn against: llama3.1:70b

2. **Standard Laptop** (16GB RAM, integrated GPU)
   - Should recommend: llama3.1:8b, mistral:7b
   - Should warn against: 70B models

3. **Mac Studio** (64GB RAM, M2 Ultra)
   - Should recommend: llama3.1:70b, qwen2.5:32b
   - Should note: Excellent for LLMs

4. **Workstation** (128GB RAM, RTX 4090)
   - Should recommend: Largest available models
   - Should note: High VRAM available

---

## Future Enhancements

1. **Real-time monitoring** - Show RAM/GPU usage during generation
2. **Performance benchmarks** - Track tokens/second per model
3. **Auto-optimization** - Suggest quantization levels
4. **Cloud recommendations** - Suggest cloud GPUs for large models
5. **Model comparison** - Show speed vs quality tradeoffs

---

**Version**: 3.0 (Planned)  
**Status**: 📋 Design Phase  
**Priority**: Medium  
**Estimated Effort**: 2-3 weeks
