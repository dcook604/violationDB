import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import API from "../../api";
// Import directly from public folder instead
// import spectrum4Logo from "../../assets/images/spectrum4-logo.png";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [logoError, setLogoError] = useState(null);
  const navigate = useNavigate();
  const { login } = useAuth();
  
  // Use an absolute path from the public folder
  const logoPath = "/spectrum4-logo.png";
  
  // Base64 encoded version of the logo as fallback
  const logoBase64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAABkCAYAAAA8AQ3AAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6OEI5RDc5RDY3NjAxMTFFOUI0QTk4RjYwQUMzQUQwMEIiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6OEI5RDc5RDc3NjAxMTFFOUI0QTk4RjYwQUMzQUQwMEIiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo4QjlENzlENDc2MDExMUU5QjRBOThGNjBBQzNBRDAwQiIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDo4QjlENzlENTc2MDExMUU5QjRBOThGNjBBQzNBRDAwQiIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PnRj7mUAAAWqSURBVHja7J1NbBVFFMd3oRRCi6XWmgDSQiXxg9iqiTGRhYkhwYUkLkzcGs0x0YUmaowmJroySjRuCCYmujFqTEjcIG5caAyfoiYqihgNUgvFQmuhlOdjTji2j/fee2/evHlz5v+TJqXtvM6d85/fnDNnZm7LwsKCcZxms+kOJz3aR8+rbY2eU0HLKVBC/bRN9PwhPe+eH/5fE/w4jtlmHTJmC1Kwwqh+jGbTdTH3SQpMMqfL+AvG26/CQPvpnEpqT6etK1UhZ/RsZ8qqgPbPdlNfxXWCTuVMVSG6PUdVYcpx36oCaFNWEZqE/UwC10/l1DH1pqByOJVT2VTC2/M6t3OPqDRDlNVRYbxu9xEfZv02GRxBOVFWPcmcQs4JKavxoG3ylmC/G5KoWCZf9kFZEX+UrfWZ9kRZbShZPyirTlnjhLJKeXlOuFhCMjAMK42sMHe0WVsLskrRJ4OjlNc9IRmYMJemjYj5JaUkZYUk7TFmdGVb56yj2GIuLVsb3cQmI3YeacvH5J9bWxtnNijAx1JpBnLQbxQgfxmXtp4ktFvfVQXnAEEZbSE1H8aJVbXEhh0m9YWdCpKB7Kb0j57vSSirhikrGH/+NRhDwkXnTNxgIqx+YX5yzuDshAx2BXWjNiGdbMPCGFDFWIeJMY38jQZl6WSVovWrxUxNHvh16xyULHRuLCclJwPz/E1jVrAYm8fZRlRp7Wlgr1NKXjd53IblaU4lH/QpzMZnKGX1xI+k16/OGe05LlPLbZSe92VqeYmvzhkVJgP1UzCfYlNWEcmAyqsavOxOAh0NlcK5I+XN0CcsnTP97SXNbEwu0Nj7qcl3u0n97Cj3CUBZgUxZpA3CSplqtX0QVpyzYdOxWTBuPmiFglB5u/AeLeaOJpk7Gma7GiTh2VFUfepXlXPvV2f6LNnDsj41sGD/ijYZ+A4FazXZpxTWo67n4Nz39H+Fj2dZM5I8wzIlZ1QrCWeVFGzwVnZzSRCsWemcUQ6FScKzI+e+8rBo3xphJd1vXjnTDr+HhQoFOqcKrTPpnJ2tLXTuPO5QgJpXVkUXxCbdF+ic0TnsZu5ozLQtK6v19yAsnQz2JNwvvGdkMsDWBW1SHR4WqhhZoXPG2mSgglX5Zk0q0H2Bzpmzc36GBcyMqsZ7ZdXrZ1jgbHBW0zFe/P5a8YPRHsIG0D7RjMrJnGqBLlEw8Y63a2wqhJVnzqjEvbIaYE610bmjs6a5zrCZVuW0l+RuDTJ35N2P3vewgLaO1uicgc4ZpSUL546Q87xmWBVGZuZYc0eQgb+UJAMlKCuQYt6nrKUU9snV1Jz7KsiqXmxMYa0hh1Pxc+5Bz7mdYSEZGLfOIZdTaTI4rtfYkJuz+i0IitZFE78Hp9fJgOqJFD9ntBxZLZUMLJjyJINF+21kMlCHsLz+MU5qVeqcqXM/fLfYDKvI3JGvOdXKJs+2GvgFIIuCUU60VaHYvZBZJr3LyB213Q93LvVLp1lYCo4/V1bJY6ltbW2VOrfP+GVBvJ2NXaGsUg49VeFxBGV1xKTbC1jU8FMm/xZT9NxR17nDwNPG81lYg0YFUS8VxmtVvE+nraJ2YLwB2BxcEAj2sKp2nrhKBkrcX0c8C9ZphBWtvIYCWa0YSjRYLKcS4mVa58pqxVmXjWGFZTXI2F/KZGCS7RFuoqw5kDFHIwPOCB9lGUm5XVIGsuA9rLxwLbAiE1oKMlhvp7rXk4ElZA+rSDKQdeQtU1aFzmVd6z1hMrACtGm/YYtJBtSu/xQ1h1g6GWgy3sMq6OQq2GVJQGfZBpVREXWTgdzDSjh0Vrif50KyVFnNuJYMyHiPnAxkDyvO0CuVlTqXUjdldTrgpaxMCckAHBcQFgCEBQAQLPj/Afa0YeJ+kS7RAAAAAElFTkSuQmCC";
  
  useEffect(() => {
    // Log when component mounts to help with debugging
    console.log("Login component mounted");
    
    // Check if logo exists by trying to load it
    const img = new Image();
    img.onerror = () => {
      setLogoError("Failed to load logo");
      console.error("Failed to load logo from path:", logoPath);
    };
    img.onload = () => {
      console.log("Logo loaded successfully with dimensions:", img.width, "x", img.height);
      setLogoError(null);
    };
    img.src = logoPath;
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    
    if (!email || !password) {
      setError("Email and password are required");
      return;
    }

    try {
      // Call the login function directly with credentials
      await login({ email, password });
      // Navigation is handled in the AuthContext
    } catch (err) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError("Login failed. Please check your credentials.");
      }
    }
  };

  // CSS styles to ensure the logo displays properly regardless of theme
  const logoContainerStyles = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: '20px',
    minHeight: '80px', // Reduced from 120px
    background: 'white', // Force white background
    padding: '10px',
    borderRadius: '5px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)' // Light shadow for visual separation
  };

  const logoStyles = {
    maxWidth: '100%',
    width: 'auto',
    height: 'auto',
    display: 'block',
    objectFit: 'contain',
    visibility: 'visible', // Force visibility
    opacity: '1', // Force opacity
    minWidth: '150px' // Ensure logo has a minimum width
  };

  return (
    <>
      <div className="container mx-auto px-4 h-full">
        <div className="flex content-center items-center justify-center h-full">
          <div className="w-full lg:w-4/12 px-4">
            <div className="relative flex flex-col min-w-0 break-words w-full mb-6 shadow-lg rounded-lg bg-white border-0">
              <div className="rounded-t mb-0 px-6 py-6">
                {/* Logo container with explicit styles */}
                <div style={logoContainerStyles}>
                  {/* Try to use the file path first, fallback to base64 if that fails */}
                  <img 
                    src={logoError ? logoBase64 : logoPath}
                    alt="Spectrum 4 Logo" 
                    style={logoStyles}
                    onError={(e) => {
                      console.error("Both logo sources failed to load");
                      // If even the base64 fails, show fallback
                      // Set fallback styling to ensure something displays
                      e.target.style.border = '1px solid #e5e5e5';
                      e.target.style.width = '200px';
                      e.target.style.height = '60px';
                      e.target.style.background = '#f5f5f5';
                      // Add a text fallback inside the image area
                      e.target.style.display = 'flex';
                      e.target.style.justifyContent = 'center';
                      e.target.style.alignItems = 'center';
                      e.target.style.fontSize = '16px';
                      e.target.style.fontWeight = 'bold';
                      e.target.style.color = '#333';
                      e.target.innerText = 'Spectrum 4';
                    }}
                  />
                  {logoError && (
                    <div className="text-red-500 text-xs mt-2">
                      Logo could not be loaded from path.
                    </div>
                  )}
                </div>
                <div className="text-center mb-3">
                  <h6 className="text-blueGray-500 text-sm font-bold">
                    Sign in with credentials
                  </h6>
                </div>
                <hr className="mt-6 border-b-1 border-blueGray-300" />
              </div>
              <div className="flex-auto px-4 lg:px-10 py-10 pt-0">
                <form onSubmit={handleSubmit}>
                  <div className="relative w-full mb-3">
                    <label
                      className="block uppercase text-blueGray-600 text-xs font-bold mb-2"
                      htmlFor="email"
                    >
                      Email
                    </label>
          <input
                      id="email"
            type="email"
                      className="border-0 px-3 py-3 placeholder-blueGray-300 text-blueGray-600 bg-white rounded text-sm shadow focus:outline-none focus:ring w-full ease-linear transition-all duration-150"
            placeholder="Email"
            value={email}
                      onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

                  <div className="relative w-full mb-3">
                    <label
                      className="block uppercase text-blueGray-600 text-xs font-bold mb-2"
                      htmlFor="password"
                    >
                      Password
                    </label>
          <input
                      id="password"
            type="password"
                      className="border-0 px-3 py-3 placeholder-blueGray-300 text-blueGray-600 bg-white rounded text-sm shadow focus:outline-none focus:ring w-full ease-linear transition-all duration-150"
            placeholder="Password"
            value={password}
                      onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

                  <div className="text-center mt-6">
                    <button
                      className="bg-lightBlue-500 text-white active:bg-lightBlue-600 text-sm font-bold uppercase px-6 py-3 rounded shadow hover:shadow-lg outline-none focus:outline-none mr-1 mb-1 w-full ease-linear transition-all duration-150"
                      type="submit"
                    >
                      Sign In
                    </button>
                  </div>
                  {error && (
                    <div className="text-red-500 text-center text-sm font-semibold mt-4">
                      {error}
                    </div>
                  )}
      </form>
    </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
} 