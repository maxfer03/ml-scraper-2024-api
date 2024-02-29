def getDomain(tld):
  domains = [
    ('ar', 'listado.mercadolibre.com.ar'),
    ('uy', 'listado.mercadolibre.com.uy'),
    ('cl', 'listado.mercadolibre.cl'),
    ('br', 'lista.mercadolivre.com.br'),
  ]
  
  domain = [x for x in domains if x[0] == tld]

  if(len(domain) == 0):
    return domains[0][1]

  return domain[0][1]
