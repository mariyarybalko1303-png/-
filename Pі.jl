using Plots

function visualize_pi(n)
    x, y = rand(n), rand(n)
    inside = x.^2 .+ y.^2 .<= 1.0
    
    scatter(x[inside], y[inside], c=:blue, label="Усередині", aspect_ratio=:equal, markersize=2)
    scatter!(x[.!inside], y[.!inside], c=:red, label="Зовні", title="Оцінка Pi: $(4 * sum(inside)/n)")
end

display(visualize_pi(2000))