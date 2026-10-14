# Integración con Flutter - Subida de Imágenes

## Endpoints disponibles

### 1. Subir solo imagen (Recomendado)
```
POST /products/upload-image
Content-Type: multipart/form-data
Authorization: Bearer {token}
```

**Uso recomendado:** Primero subir la imagen, obtener la URL, y luego crear el producto con la URL.

**Ejemplo Flutter:**
```dart
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'dart:io';

Future<String?> uploadImage(File imageFile, String token) async {
  final uri = Uri.parse('http://tu-api.com/products/upload-image');
  
  var request = http.MultipartRequest('POST', uri);
  request.headers['Authorization'] = 'Bearer $token';
  
  // Agregar la imagen
  request.files.add(
    await http.MultipartFile.fromPath('file', imageFile.path)
  );
  
  final response = await request.send();
  
  if (response.statusCode == 200) {
    final responseData = await response.stream.bytesToString();
    final json = jsonDecode(responseData);
    return json['image_url'];
  }
  return null;
}

// Luego crear el producto con la URL
Future<void> createProduct(String imageUrl, String token) async {
  final response = await http.post(
    Uri.parse('http://tu-api.com/products'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'name': 'Producto',
      'description': 'Descripción',
      'price': 99.99,
      'stock': 10,
      'is_active': true,
      'image_url': imageUrl,
    }),
  );
}
```

### 2. Crear producto con imagen (Todo en uno)
```
POST /products/with-image
Content-Type: multipart/form-data
Authorization: Bearer {token}
```

**Campos del formulario:**
- `name` (required): string
- `price` (required): float
- `stock` (required): int
- `description` (optional): string
- `is_active` (optional): bool
- `image` (optional): file

**Ejemplo Flutter:**
```dart
Future<void> createProductWithImage(File? imageFile, String token) async {
  final uri = Uri.parse('http://tu-api.com/products/with-image');
  
  var request = http.MultipartRequest('POST', uri);
  request.headers['Authorization'] = 'Bearer $token';
  
  // Agregar campos de texto
  request.fields['name'] = 'Nombre del producto';
  request.fields['description'] = 'Descripción del producto';
  request.fields['price'] = '99.99';
  request.fields['stock'] = '10';
  request.fields['is_active'] = 'true';
  
  // Agregar imagen si existe
  if (imageFile != null) {
    request.files.add(
      await http.MultipartFile.fromPath('image', imageFile.path)
    );
  }
  
  final response = await request.send();
  
  if (response.statusCode == 201) {
    print('Producto creado exitosamente');
  }
}
```

### 3. Actualizar solo la imagen de un producto
```
PUT /products/{product_id}/image
Content-Type: multipart/form-data
Authorization: Bearer {token}
```

**Ejemplo Flutter:**
```dart
Future<void> updateProductImage(int productId, File imageFile, String token) async {
  final uri = Uri.parse('http://tu-api.com/products/$productId/image');
  
  var request = http.MultipartRequest('PUT', uri);
  request.headers['Authorization'] = 'Bearer $token';
  
  request.files.add(
    await http.MultipartFile.fromPath('file', imageFile.path)
  );
  
  final response = await request.send();
  
  if (response.statusCode == 200) {
    print('Imagen actualizada');
  }
}
```

## Ejemplo completo - Selector de imagen Flutter

```dart
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'dart:convert';

class ProductService {
  final String baseUrl = 'http://tu-api.com';
  final ImagePicker _picker = ImagePicker();
  
  // Seleccionar imagen de galería o cámara
  Future<File?> pickImage(ImageSource source) async {
    final XFile? image = await _picker.pickImage(
      source: source,
      imageQuality: 70, // Comprimir al 70%
    );
    
    if (image != null) {
      return File(image.path);
    }
    return null;
  }
  
  // Opción 1: Subir imagen primero, luego crear producto
  Future<Map<String, dynamic>?> createProductWithImageUrl(
    File imageFile,
    Map<String, dynamic> productData,
    String token,
  ) async {
    try {
      // 1. Subir imagen
      final imageUrl = await uploadImage(imageFile, token);
      if (imageUrl == null) return null;
      
      // 2. Agregar URL al producto
      productData['image_url'] = imageUrl;
      
      // 3. Crear producto
      final response = await http.post(
        Uri.parse('$baseUrl/products'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode(productData),
      );
      
      if (response.statusCode == 201) {
        return jsonDecode(response.body);
      }
    } catch (e) {
      print('Error: $e');
    }
    return null;
  }
  
  Future<String?> uploadImage(File imageFile, String token) async {
    final uri = Uri.parse('$baseUrl/products/upload-image');
    
    var request = http.MultipartRequest('POST', uri);
    request.headers['Authorization'] = 'Bearer $token';
    
    request.files.add(
      await http.MultipartFile.fromPath('file', imageFile.path)
    );
    
    final response = await request.send();
    
    if (response.statusCode == 200) {
      final responseData = await response.stream.bytesToString();
      final json = jsonDecode(responseData);
      return json['image_url'];
    }
    return null;
  }
}
```

## Widget de ejemplo Flutter

```dart
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

class CreateProductScreen extends StatefulWidget {
  @override
  _CreateProductScreenState createState() => _CreateProductScreenState();
}

class _CreateProductScreenState extends State<CreateProductScreen> {
  File? _imageFile;
  final _nameController = TextEditingController();
  final _priceController = TextEditingController();
  final _stockController = TextEditingController();
  final ProductService _service = ProductService();
  
  Future<void> _pickImage() async {
    final source = await showDialog<ImageSource>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Seleccionar imagen'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, ImageSource.camera),
            child: Text('Cámara'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, ImageSource.gallery),
            child: Text('Galería'),
          ),
        ],
      ),
    );
    
    if (source != null) {
      final image = await _service.pickImage(source);
      setState(() => _imageFile = image);
    }
  }
  
  Future<void> _createProduct() async {
    if (_imageFile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Selecciona una imagen')),
      );
      return;
    }
    
    final productData = {
      'name': _nameController.text,
      'price': double.parse(_priceController.text),
      'stock': int.parse(_stockController.text),
      'is_active': true,
    };
    
    final token = 'tu_token_aqui'; // Obtener del storage
    
    final result = await _service.createProductWithImageUrl(
      _imageFile!,
      productData,
      token,
    );
    
    if (result != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Producto creado exitosamente')),
      );
      Navigator.pop(context);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Crear Producto')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            // Imagen
            GestureDetector(
              onTap: _pickImage,
              child: Container(
                height: 200,
                width: double.infinity,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: _imageFile != null
                    ? Image.file(_imageFile!, fit: BoxFit.cover)
                    : Icon(Icons.add_photo_alternate, size: 50),
              ),
            ),
            SizedBox(height: 16),
            
            // Campos
            TextField(
              controller: _nameController,
              decoration: InputDecoration(labelText: 'Nombre'),
            ),
            TextField(
              controller: _priceController,
              decoration: InputDecoration(labelText: 'Precio'),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: _stockController,
              decoration: InputDecoration(labelText: 'Stock'),
              keyboardType: TextInputType.number,
            ),
            
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _createProduct,
              child: Text('Crear Producto'),
            ),
          ],
        ),
      ),
    );
  }
}
```

## Dependencias Flutter necesarias

```yaml
dependencies:
  http: ^1.1.0
  image_picker: ^1.0.4
```

## Notas importantes

1. **Formatos soportados**: JPG, JPEG, PNG, GIF, WEBP
2. **Autenticación**: Todos los endpoints requieren rol "admin"
3. **Tamaño**: Recomendado comprimir imágenes antes de subir (imageQuality: 70)
4. **URL base**: Reemplazar `http://tu-api.com` con tu URL real
5. **Token**: Guardar el token después del login y usarlo en cada petición
