function Final = RidgeGDeS(x, y, k,alpha)


m = length(y); % store the number of training examples
x = [ones(m, 1), x]; % Add a column of ones to x
n = size(x,2);
theta_vec_new = ones(size(x,2),1).*0
theta_vec_cur = ones(size(x,2),1).*0.5


while (abs(theta_vec_cur - theta_vec_new) > 0.0000000000000001)
 theta_vec_cur = theta_vec_new
 h_theta = (x*theta_vec_cur);
 h_theta_v = h_theta*ones(1,n);
 y_v = y*ones(1,n);
 theta_vec_new = theta_vec_cur*(1-alpha*k/m) - alpha*1/m*sum((h_theta_v - y_v).*x).';
end

Final = theta_vec_new;

end
